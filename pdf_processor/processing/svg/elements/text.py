""
SVG text element generators.
"""
from typing import Dict, List, Optional, Tuple, Union, Any
from xml.etree import ElementTree as ET

from ...models.ocr_result import TextBlock, TextLine, TextWord

def create_text_element(
    x: Union[int, float, str],
    y: Union[int, float, str],
    text: str,
    font_family: str = "Arial, sans-serif",
    font_size: Union[int, float, str] = 12,
    fill: str = "#000000",
    text_anchor: str = "start",
    dominant_baseline: str = "auto",
    **attrs
) -> ET.Element:
    """Create an SVG text element.
    
    Args:
        x: X coordinate of the text anchor point.
        y: Y coordinate of the text baseline.
        text: The text content.
        font_family: Font family or list of font families.
        font_size: Font size in pixels.
        fill: Text color.
        text_anchor: Horizontal alignment (start, middle, end).
        dominant_baseline: Vertical alignment (auto, middle, hanging, etc.).
        **attrs: Additional SVG attributes.
        
    Returns:
        An SVG text element.
    """
    attrs.update({
        'x': str(x),
        'y': str(y),
        'font-family': font_family,
        'font-size': str(font_size),
        'fill': fill,
        'text-anchor': text_anchor,
        'dominant-baseline': dominant_baseline
    })
    
    text_elem = ET.Element('text', **attrs)
    text_elem.text = text
    return text_elem

def create_text_block(
    block: TextBlock,
    font_family: str = "Arial, sans-serif",
    font_size: Union[int, float, str] = 12,
    fill: str = "#000000",
    show_bbox: bool = False,
    **attrs
) -> ET.Element:
    """Create an SVG group containing text elements for a text block.
    
    Args:
        block: The text block to render.
        font_family: Font family or list of font families.
        font_size: Base font size in pixels.
        fill: Text color.
        show_bbox: Whether to show the bounding box for debugging.
        **attrs: Additional SVG attributes for the group.
        
    Returns:
        An SVG group element containing the text elements.
    """
    group_attrs = {
        'class': 'text-block',
        'data-block-id': str(getattr(block, 'id', '')),
        'data-confidence': str(getattr(block, 'confidence', 1.0))
    }
    group_attrs.update(attrs)
    
    group = ET.Element('g', **group_attrs)
    
    # Add bounding box if requested
    if show_bbox and hasattr(block, 'bbox') and block.bbox:
        bbox = block.bbox
        ET.SubElement(group, 'rect', {
            'x': str(bbox[0]),
            'y': str(bbox[1]),
            'width': str(bbox[2] - bbox[0]),
            'height': str(bbox[3] - bbox[1]),
            'fill': 'none',
            'stroke': 'red',
            'stroke-width': '1',
            'opacity': '0.5'
        })
    
    # Add text elements for each line
    for line in getattr(block, 'lines', []):
        if not hasattr(line, 'words') or not line.words:
            continue
            
        # Create a line group
        line_group = ET.SubElement(group, 'g', {
            'class': 'text-line',
            'data-line-id': str(getattr(line, 'id', ''))
        })
        
        # Add each word
        for word in line.words:
            if not hasattr(word, 'text') or not word.text:
                continue
                
            word_attrs = {
                'class': 'text-word',
                'data-word': word.text,
                'data-confidence': str(getattr(word, 'confidence', 1.0))
            }
            
            # Add word bounding box if available
            if hasattr(word, 'bbox') and word.bbox:
                word_attrs.update({
                    'data-x': str(word.bbox[0]),
                    'data-y': str(word.bbox[1]),
                    'data-width': str(word.bbox[2] - word.bbox[0]),
                    'data-height': str(word.bbox[3] - word.bbox[1])
                })
            
            # Create text element for the word
            text_elem = create_text_element(
                x=word.bbox[0] if hasattr(word, 'bbox') and word.bbox else 0,
                y=word.bbox[3] if hasattr(word, 'bbox') and word.bbox else font_size,
                text=word.text + ' ',
                font_family=font_family,
                font_size=font_size,
                fill=fill,
                **word_attrs
            )
            
            line_group.append(text_elem)
    
    return group
