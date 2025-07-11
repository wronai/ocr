#!/usr/bin/env python3
"""
PDF OCR Processor - Command Line Interface

This module provides the command line interface for the PDF OCR Processor.
It allows running the package directly with `python -m pdf_processor`.
"""
import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
