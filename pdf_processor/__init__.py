"""
PDF OCR Processor - Advanced PDF text extraction with AI

This package provides powerful OCR capabilities for PDF documents
using Ollama AI models with automatic SVG generation and metadata.
"""

import logging
from pathlib import Path
from typing import Optional, Union

# Import version
from .__version__ import __version__

# Import core components
from .models.ocr_result import OCRResult, TextBlock
from .models.retry_config import RetryConfig

# Import processing components
from .processing.pdf_processor import PDFProcessor, PDFProcessorConfig
from .processing.image_enhancement import ImageEnhancer, EnhancementStrategy
from .processing.ocr_processor import OCRProcessor
from .processing.svg_generator import SVGGenerator, SVGConfig

# Import CLI
from .cli import main

# Set up default logger
logger = logging.getLogger(__name__)

def setup_logging(level=logging.INFO, log_file: Optional[Union[str, Path]] = None):
    """Configure logging for the application.
    
    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Optional path to a log file
    """
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logging.root.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logging.root.addHandler(file_handler)
    
    # Set the logging level
    logging.root.setLevel(level)

__all__ = [
    # Core classes
    "PDFProcessor",
    "PDFProcessorConfig",
    "OCRProcessor",
    "OCRResult",
    "TextBlock",
    "RetryConfig",
    "ImageEnhancer",
    "EnhancementStrategy",
    "SVGGenerator",
    "SVGConfig",
    
    # Functions
    "main",
    "setup_logging",
    
    # Version
    "__version__"
]

# Set up default logging when the package is imported
setup_logging()

__author__ = "PDF OCR Processor Team"
__email__ = "team@pdf-ocr-processor.com"
__license__ = "Apache-2.0"
__copyright__ = "Copyright 2025 PDF OCR Processor Contributors"
