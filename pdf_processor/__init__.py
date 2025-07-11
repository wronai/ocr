"""
PDF OCR Processor - Advanced PDF text extraction with AI

This package provides powerful OCR capabilities for PDF documents
using Ollama AI models with automatic SVG generation and metadata.
"""

from .pdf_processor import PDFOCRProcessor, main
from .__version__ import __version__
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_logging(level=logging.INFO):
    """Configure logging for the application."""
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

__all__ = [
    "PDFOCRProcessor",
    "main",
    "logger",
    "setup_logging",
    "__version__",
]

# Package metadata
__author__ = "PDF OCR Processor Team"
__email__ = "team@pdf-ocr-processor.com"
__license__ = "Apache-2.0"
__copyright__ = "Copyright 2025 PDF OCR Processor Contributors"


