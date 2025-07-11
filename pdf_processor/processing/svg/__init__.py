"""SVG generation modules for OCR results.

This package provides functionality to generate SVG files from OCR results,
including support for both single and multi-page documents with interactive
elements like text selection and navigation controls.
"""

from .base_generator import SVGGenerator, SVGConfig
from .page_generator import generate_svg_page
from .multipage_generator import generate_multi_page_svg

__all__ = [
    'SVGGenerator',
    'SVGConfig',
    'generate_svg_page',
    'generate_multi_page_svg'
]
