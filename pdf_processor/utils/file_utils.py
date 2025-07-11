"""File utility functions for the PDF OCR Processor."""

import os
import shutil
import tempfile
import hashlib
from pathlib import Path
from typing import Union, List, Optional, Tuple, BinaryIO, Generator
from PIL import Image
import fitz  # PyMuPDF

from ..config.settings import SUPPORTED_IMAGE_FORMATS


def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
        
    Returns:
        Path: The path as a Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_hash(file_path: Union[str, Path], chunk_size: int = 8192) -> str:
    """Calculate the MD5 hash of a file.
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read at a time
        
    Returns:
        str: The MD5 hash of the file
    """
    file_path = Path(file_path)
    hasher = hashlib.md5()
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def create_temp_file(suffix: str = '.tmp', dir: Optional[Union[str, Path]] = None) -> Path:
    """Create a temporary file and return its path.
    
    Args:
        suffix: File suffix/extension
        dir: Directory to create the temp file in
        
    Returns:
        Path: Path to the created temporary file
    """
    if dir is not None:
        dir = str(Path(dir).absolute())
    
    fd, path = tempfile.mkstemp(suffix=suffix, dir=dir)
    os.close(fd)
    return Path(path)


def cleanup_temp_files(temp_files: List[Union[str, Path]]) -> None:
    """Remove temporary files.
    
    Args:
        temp_files: List of paths to temporary files to remove
    """
    for path in temp_files:
        try:
            path = Path(path)
            if path.exists():
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not remove temp file {path}: {e}")


def is_image_file(file_path: Union[str, Path]) -> bool:
    """Check if a file is a supported image file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if the file is a supported image, False otherwise
    """
    file_path = Path(file_path)
    return file_path.suffix.lower() in SUPPORTED_IMAGE_FORMATS


def pdf_to_images(pdf_path: Union[str, Path], dpi: int = 300) -> List[Path]:
    """Convert a PDF to a list of image files.
    
    Args:
        pdf_path: Path to the PDF file
        dpi: DPI for the output images
        
    Returns:
        List[Path]: List of paths to the generated image files
    """
    pdf_path = Path(pdf_path)
    output_dir = pdf_path.parent / f"{pdf_path.stem}_pages"
    output_dir.mkdir(exist_ok=True)
    
    image_paths = []
    
    try:
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc, 1):
            # Render page to an image
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            img_path = output_dir / f"page_{i:03d}.png"
            
            # Save as PNG
            pix.save(str(img_path))
            image_paths.append(img_path)
            
    except Exception as e:
        # Clean up any partially created images
        cleanup_temp_files(image_paths)
        raise RuntimeError(f"Failed to convert PDF to images: {e}")
    
    return image_paths


def save_image(image: Image.Image, output_path: Union[str, Path], **kwargs) -> Path:
    """Save an image to disk.
    
    Args:
        image: PIL Image to save
        output_path: Path to save the image to
        **kwargs: Additional arguments to pass to Image.save()
        
    Returns:
        Path: The path the image was saved to
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Default to PNG if no format is specified
    if 'format' not in kwargs and not output_path.suffix:
        kwargs['format'] = 'PNG'
    
    image.save(output_path, **kwargs)
    return output_path


def get_image_size(image_path: Union[str, Path]) -> Tuple[int, int]:
    """Get the dimensions of an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple[int, int]: (width, height) of the image
    """
    with Image.open(image_path) as img:
        return img.size
