""
Utility functions for SVG generation.

This package contains utility modules for working with SVG, including:
- SVG-specific utilities
- Style handling
- XML manipulation
- Coordinate transformations
"""

from .svg_utils import (
    svg_escape,
    create_svg_element,
    create_svg_group,
    create_svg_style,
    create_svg_script,
    pretty_print_xml
)

from .style_utils import (
    create_css_style,
    merge_styles,
    style_to_dict,
    dict_to_style
)

__all__ = [
    'svg_escape',
    'create_svg_element',
    'create_svg_group',
    'create_svg_style',
    'create_svg_script',
    'pretty_print_xml',
    'create_css_style',
    'merge_styles',
    'style_to_dict',
    'dict_to_style'
]
