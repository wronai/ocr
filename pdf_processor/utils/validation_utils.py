"""Validation utilities for the PDF OCR Processor."""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Type, TypeVar
from dataclasses import is_dataclass, asdict
import json

from PIL import Image
import fitz  # PyMuPDF

from ..models.ocr_result import OCRResult, TextBlock
from ..config.settings import SUPPORTED_IMAGE_FORMATS

T = TypeVar('T')


def validate_path(
    path: Union[str, Path], 
    must_exist: bool = True, 
    must_be_file: bool = False,
    must_be_dir: bool = False,
    create_if_missing: bool = False
) -> Path:
    """Validate a filesystem path.
    
    Args:
        path: The path to validate
        must_exist: If True, the path must exist
        must_be_file: If True, the path must be a file
        must_be_dir: If True, the path must be a directory
        create_if_missing: If True and must_be_dir is True, create the directory if it doesn't exist
        
    Returns:
        Path: The validated Path object
        
    Raises:
        ValueError: If the path is invalid
        FileNotFoundError: If the path must exist but doesn't
        NotADirectoryError: If the path must be a directory but isn't
        IsADirectoryError: If the path must be a file but is a directory
    """
    path = Path(path).expanduser().resolve()
    
    if must_exist and not path.exists():
        if must_be_dir and create_if_missing:
            path.mkdir(parents=True, exist_ok=True)
            return path
        raise FileNotFoundError(f"Path does not exist: {path}")
    
    if must_be_file and not path.is_file():
        if path.exists():
            raise IsADirectoryError(f"Path is a directory, expected a file: {path}")
        raise FileNotFoundError(f"File does not exist: {path}")
    
    if must_be_dir and not path.is_dir():
        if path.exists():
            raise NotADirectoryError(f"Path is a file, expected a directory: {path}")
        raise NotADirectoryError(f"Directory does not exist: {path}")
    
    return path


def validate_pdf_file(path: Union[str, Path]) -> Path:
    """Validate that a file is a PDF.
    
    Args:
        path: Path to the PDF file
        
    Returns:
        Path: The validated Path object
        
    Raises:
        ValueError: If the file is not a PDF or is invalid
    """
    path = validate_path(path, must_exist=True, must_be_file=True)
    
    if path.suffix.lower() != '.pdf':
        raise ValueError(f"File is not a PDF: {path}")
    
    try:
        # Try to open the PDF to check if it's valid
        with fitz.open(path) as doc:
            if doc.page_count == 0:
                raise ValueError(f"PDF has no pages: {path}")
    except Exception as e:
        raise ValueError(f"Invalid PDF file {path}: {e}")
    
    return path


def validate_image_file(path: Union[str, Path]) -> Path:
    """Validate that a file is a supported image.
    
    Args:
        path: Path to the image file
        
    Returns:
        Path: The validated Path object
        
    Raises:
        ValueError: If the file is not a supported image or is invalid
    """
    path = validate_path(path, must_exist=True, must_be_file=True)
    
    if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
        raise ValueError(
            f"Unsupported image format: {path.suffix}. "
            f"Supported formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
        )
    
    try:
        # Try to open the image to check if it's valid
        with Image.open(path) as img:
            img.verify()
    except Exception as e:
        raise ValueError(f"Invalid image file {path}: {e}")
    
    return path


def validate_ocr_result(data: Dict[str, Any]) -> OCRResult:
    """Validate and normalize an OCR result dictionary.
    
    Args:
        data: The OCR result data to validate
        
    Returns:
        OCRResult: A validated and normalized OCR result
        
    Raises:
        ValueError: If the data is invalid
    """
    if not isinstance(data, dict):
        raise ValueError(f"OCR result must be a dictionary, got {type(data).__name__}")
    
    # Normalize the data
    result = {
        'text': str(data.get('text', '')),
        'language': str(data.get('language', 'pl')),
        'confidence': float(data.get('confidence', 0.0)),
        'model': str(data.get('model', 'unknown')),
        'metadata': dict(data.get('metadata', {})),
        'blocks': []
    }
    
    # Validate blocks if present
    if 'blocks' in data and isinstance(data['blocks'], list):
        for i, block_data in enumerate(data['blocks']):
            try:
                if not isinstance(block_data, dict):
                    raise ValueError(f"Block at index {i} is not a dictionary")
                
                block = {
                    'text': str(block_data.get('text', '')),
                    'x': float(block_data.get('x', 0)),
                    'y': float(block_data.get('y', 0)),
                    'width': max(0, float(block_data.get('width', 0))),
                    'height': max(0, float(block_data.get('height', 0))),
                    'confidence': min(1.0, max(0, float(block_data.get('confidence', 1.0)))),
                    'language': str(block_data.get('language', result['language'])),
                    'metadata': dict(block_data.get('metadata', {}))
                }
                
                result['blocks'].append(block)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid block at index {i}: {e}")
    
    # If no blocks but we have text, create a single block
    if not result['blocks'] and result['text'].strip():
        result['blocks'].append({
            'text': result['text'],
            'x': 0,
            'y': 0,
            'width': 0,
            'height': 0,
            'confidence': result['confidence'],
            'language': result['language'],
            'metadata': {}
        })
    
    # Calculate confidence if not provided
    if result['confidence'] <= 0 and result['blocks']:
        result['confidence'] = sum(b['confidence'] for b in result['blocks']) / len(result['blocks'])
    
    return OCRResult(**result)


def validate_positive_number(
    value: Any, 
    name: str, 
    min_value: float = 0, 
    max_value: Optional[float] = None
) -> float:
    """Validate that a value is a positive number within a range.
    
    Args:
        value: The value to validate
        name: Name of the parameter for error messages
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)
        
    Returns:
        float: The validated number
        
    Raises:
        ValueError: If the value is invalid
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a number, got {value!r}")
    
    if num < min_value:
        raise ValueError(f"{name} must be >= {min_value}, got {num}")
    
    if max_value is not None and num > max_value:
        raise ValueError(f"{name} must be <= {max_value}, got {num}")
    
    return num


def validate_enum_value(
    value: Any, 
    enum_values: list, 
    name: str,
    case_sensitive: bool = False
) -> Any:
    """Validate that a value is one of the allowed enum values.
    
    Args:
        value: The value to validate
        enum_values: List of allowed values
        name: Name of the parameter for error messages
        case_sensitive: Whether the comparison should be case-sensitive
        
    Returns:
        The validated value
        
    Raises:
        ValueError: If the value is not in the allowed values
    """
    if not case_sensitive and isinstance(value, str):
        value_lower = value.lower()
        for ev in enum_values:
            if isinstance(ev, str) and ev.lower() == value_lower:
                return ev
    
    if value not in enum_values:
        raise ValueError(
            f"{name} must be one of {enum_values}, got {value!r}"
        )
    
    return value
