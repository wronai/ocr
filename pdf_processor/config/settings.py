"""Configuration settings and constants for the PDF OCR Processor."""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent.parent
DOCUMENTS_FOLDER = os.getenv("DOCUMENTS_FOLDER", str(BASE_DIR / "documents"))
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", str(BASE_DIR / "output"))

# Default model settings
DEFAULT_OCR_MODEL = "llava:7b"
SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp']

# Processing settings
DEFAULT_TIMEOUT = 900  # 15 minutes (increased from 5 minutes)
MAX_WORKERS = min(4, (os.cpu_count() or 1) + 2)
MAX_IMAGE_SIZE = (4096, 4096)  # Max width, height

# Retry settings
DEFAULT_MAX_RETRIES = 2  # Reduced from 3 to prevent very long processing
INITIAL_RETRY_DELAY = 5  # Increased from 2 seconds
MAX_RETRY_DELAY = 300  # Increased from 60 seconds (5 minutes max delay)
BACKOFF_FACTOR = 2

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "pdf_processor.log"))

# OCR settings
OCR_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence score to accept OCR results

# Image enhancement settings
ENHANCEMENT_STRATEGIES = [
    'original',
    'grayscale',
    'adaptive_threshold',
    'contrast_stretch',
    'sharpen',
    'denoise'
]

# SVG generation settings
SVG_METADATA = {
    'creator': 'PDF OCR Processor',
    'generator': 'PDF OCR Processor',
    'version': '2.0.0'
}
