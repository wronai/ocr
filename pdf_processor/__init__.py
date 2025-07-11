"""
PDF OCR Processor - Advanced PDF text extraction with AI

This package provides powerful OCR capabilities for PDF documents
using Ollama AI models with automatic SVG generation and metadata.
"""

from .core import PDFOCRProcessor
from .utils import logger, setup_logging
from .__version__ import __version__

__all__ = [
    "PDFOCRProcessor",
    "logger",
    "setup_logging",
    "__version__",
]

# Package metadata
__author__ = "PDF OCR Processor Team"
__email__ = "team@pdf-ocr-processor.com"
__license__ = "MIT"
__copyright__ = "Copyright 2025 PDF OCR Processor Contributors"

---

# pdf_processor/__version__.py
"""Version information for PDF OCR Processor."""

__version__ = "2.0.0"
__version_info__ = (2, 0, 0)

# Version history
CHANGELOG = {
    "2.0.0": "Complete rewrite with parallel processing, better error handling, and SVG generation",
    "1.0.0": "Initial release with basic PDF OCR functionality",
    "0.9.0": "Proof of concept and Ollama integration",
}
