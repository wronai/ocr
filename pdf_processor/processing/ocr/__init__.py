"""
OCR processing module for PDF text extraction.

This package provides functionality for extracting text from images using OCR,
with support for various OCR backends and result processing.

Modules:
    base_processor: Core OCR processing functionality
    ollama_client: Client for interacting with Ollama API
    result_parser: Utilities for parsing OCR results
    batch_processor: Batch processing of multiple images
    models: Data models and types used in OCR processing
"""

from .base_processor import OCRProcessor
from .models import OCRResult, TextBlock, BoundingBox

__all__ = [
    'OCRProcessor',
    'OCRResult',
    'TextBlock',
    'BoundingBox'
]
