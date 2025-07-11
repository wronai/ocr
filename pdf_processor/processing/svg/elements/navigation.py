""
SVG navigation elements for multi-page documents.
"""
from typing import Dict, List, Optional, Tuple, Union, Any
from xml.etree import ElementTree as ET

def create_navigation_controls(
    x: Union[int, float, str],
    y: Union[int, float, str],
    page_count: int,
    current_page: int = 0,
    button_width: Union[int, float] = 80,
    button_height: Union[int, float] = 30,
    button_rx: Union[int, float] = 4,
    button_ry: Union[int, float] = 4,
    button_fill: str = "#f0f0f0",
    button_stroke: str = "#ccc",
    button_hover_fill: str = "#e0e0e0",
    button_text_color: str = "#333",
    button_text_size: Union[int, float] = 12,
    button_spacing: Union[int, float] = 10,
    show_page_numbers: bool = True,
    **attrs
) -> ET.Element:
    """Create navigation controls for a multi-page document.
    
    Args:
        x: X coordinate of the top-left corner of the navigation bar.
        y: Y coordinate of the top-left corner of the navigation bar.
        page_count: Total number of pages.
        current_page: Current (0-based) page index.
        button_width: Width of navigation buttons.
        button_height: Height of navigation buttons.
        button_rx: X radius for button corners.
        button_ry: Y radius for button corners.
        button_fill: Button background color.
        button_stroke: Button border color.
        button_hover_fill: Button background color on hover.
        button_text_color: Button text color.
        button_text_size: Button text size in pixels.
        button_spacing: Space between buttons.
        show_page_numbers: Whether to show the page number indicator.
        **attrs: Additional SVG attributes for the navigation group.
        
    Returns:
        An SVG group element containing the navigation controls.
    """
    if page_count <= 1:
        return ET.Element('g')  # Empty group if only one page
    
    # Create navigation group
    nav_attrs = {
        'class': 'nav-controls',
        'data-page-count': str(page_count),
        'data-current-page': str(current_page)
    }
    nav_attrs.update(attrs)
    nav_group = ET.Element('g', nav_attrs)
    
    # Add style for the navigation controls
    style = """
    .nav-button {
        cursor: pointer;
        user-select: none;
    }
    .nav-button:hover {
        fill: %s;
    }
    .nav-button:active {
        filter: brightness(0.95);
    }
    .nav-disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    .nav-disabled:hover {
        fill: %s !important;
    }
    """ % (button_hover_fill, button_fill)
    
    style_elem = ET.Element('style')
    style_elem.text = style
    nav_group.append(style_elem)
    
    # Add previous button
    prev_btn = ET.Element('g', {
        'class': 'nav-button prev-button',
        'onclick': 'showPage(currentPage - 1)'
    })
    
    ET.SubElement(prev_btn, 'rect', {
        'x': str(x),
        'y': str(y),
        'width': str(button_width),
        'height': str(button_height),
        'rx': str(button_rx),
        'ry': str(button_ry),
        'fill': button_fill,
        'stroke': button_stroke,
        'class': 'nav-button-bg'
    })
    
    ET.SubElement(prev_btn, 'text', {
        'x': str(x + button_width / 2),
        'y': str(y + button_height / 2),
        'text-anchor': 'middle',
        'dominant-baseline': 'middle',
        'fill': button_text_color,
        'font-size': str(button_text_size),
        'class': 'nav-button-text'
    }).text = 'Previous'
    
    nav_group.append(prev_btn)
    
    # Add next button
    next_x = x + button_width + button_spacing
    next_btn = ET.Element('g', {
        'class': 'nav-button next-button',
        'onclick': 'showPage(currentPage + 1)'
    })
    
    ET.SubElement(next_btn, 'rect', {
        'x': str(next_x),
        'y': str(y),
        'width': str(button_width),
        'height': str(button_height),
        'rx': str(button_rx),
        'ry': str(button_ry),
        'fill': button_fill,
        'stroke': button_stroke,
        'class': 'nav-button-bg'
    })
    
    ET.SubElement(next_btn, 'text', {
        'x': str(next_x + button_width / 2),
        'y': str(y + button_height / 2),
        'text-anchor': 'middle',
        'dominant-baseline': 'middle',
        'fill': button_text_color,
        'font-size': str(button_text_size),
        'class': 'nav-button-text'
    }).text = 'Next'
    
    nav_group.append(next_btn)
    
    # Add page indicator
    if show_page_numbers:
        indicator_x = next_x + button_width + button_spacing * 2
        indicator = ET.Element('text', {
            'x': str(indicator_x),
            'y': str(y + button_height / 2),
            'text-anchor': 'start',
            'dominant-baseline': 'middle',
            'fill': button_text_color,
            'font-size': str(button_text_size),
            'class': 'page-indicator'
        })
        
        indicator.text = f"Page {current_page + 1} of {page_count}"
        nav_group.append(indicator)
    
    return nav_group

def create_page_indicator(
    x: Union[int, float, str],
    y: Union[int, float, str],
    current_page: int,
    page_count: int,
    text_color: str = "#333333",
    font_size: Union[int, float, str] = 12,
    **attrs
) -> ET.Element:
    """Create a simple page indicator (e.g., 'Page 1 of 5').
    
    Args:
        x: X coordinate of the indicator.
        y: Y coordinate of the indicator.
        current_page: Current (0-based) page index.
        page_count: Total number of pages.
        text_color: Text color.
        font_size: Font size in pixels.
        **attrs: Additional SVG attributes.
        
    Returns:
        An SVG text element showing the page indicator.
    """
    attrs.update({
        'x': str(x),
        'y': str(y),
        'text-anchor': 'start',
        'dominant-baseline': 'middle',
        'fill': text_color,
        'font-size': str(font_size),
        'class': 'page-indicator',
        'data-current-page': str(current_page),
        'data-page-count': str(page_count)
    })
    
    indicator = ET.Element('text', attrs)
    indicator.text = f"Page {current_page + 1} of {page_count}"
    
    return indicator
