""
SVG-specific utility functions.
"""
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Optional, Tuple, Union, Any

def svg_escape(text: str) -> str:
    """Escape special characters in text for use in SVG.
    
    Args:
        text: The text to escape.
        
    Returns:
        The escaped text.
    """
    if not text:
        return ""
    
    # Replace special characters with their XML entities
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    # Ensure valid XML characters (remove control characters except \t, \n, \r)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x84\x86-\x9F\uFFFE\uFFFF]', '', text)
    
    return text

def create_svg_element(
    tag: str,
    parent: Optional[ET.Element] = None,
    text: Optional[str] = None,
    tail: Optional[str] = None,
    **attrs
) -> ET.Element:
    """Create an SVG element with proper namespace handling.
    
    Args:
        tag: The element tag name.
        parent: Optional parent element to append to.
        text: Optional element text content.
        tail: Optional text after the element.
        **attrs: Element attributes.
        
    Returns:
        The created SVG element.
    """
    # Handle special case for xlink:href
    if 'xlink_href' in attrs:
        attrs['{http://www.w3.org/1999/xlink}href'] = attrs.pop('xlink_href')
    
    # Handle class attribute (convert list to space-separated string)
    if 'class_' in attrs:
        attrs['class'] = ' '.join(attrs.pop('class_')) if isinstance(attrs['class_'], (list, tuple, set)) else attrs.pop('class_')
    
    # Create the element
    element = ET.Element(tag, **{k: str(v) for k, v in attrs.items() if v is not None})
    
    # Set text and tail if provided
    if text is not None:
        element.text = str(text)
    if tail is not None:
        element.tail = str(tail)
    
    # Add to parent if provided
    if parent is not None:
        parent.append(element)
    
    return element

def create_svg_group(
    parent: Optional[ET.Element] = None,
    id: Optional[str] = None,
    class_: Optional[Union[str, List[str]]] = None,
    transform: Optional[str] = None,
    **attrs
) -> ET.Element:
    """Create an SVG group element.
    
    Args:
        parent: Optional parent element to append to.
        id: Optional element ID.
        class_: Optional class name(s).
        transform: Optional transform attribute.
        **attrs: Additional attributes.
        
    Returns:
        The created SVG group element.
    """
    attrs['id'] = id
    attrs['class'] = class_
    attrs['transform'] = transform
    
    return create_svg_element('g', parent=parent, **{
        k: v for k, v in attrs.items() if v is not None
    })

def create_svg_style(
    css: str,
    parent: Optional[ET.Element] = None,
    **attrs
) -> ET.Element:
    """Create an SVG style element.
    
    Args:
        css: CSS content.
        parent: Optional parent element to append to.
        **attrs: Additional attributes.
        
    Returns:
        The created SVG style element.
    """
    style = create_svg_element('style', parent=parent, **attrs)
    style.text = f"""/* <![CDATA[ */\n{css}\n/* ]]> */"""
    return style

def create_svg_script(
    javascript: str,
    parent: Optional[ET.Element] = None,
    **attrs
) -> ET.Element:
    """Create an SVG script element.
    
    Args:
        javascript: JavaScript content.
        parent: Optional parent element to append to.
        **attrs: Additional attributes.
        
    Returns:
        The created SVG script element.
    """
    attrs.update({
        'type': 'application/ecmascript',
        'xlink:href': 'data:,',  # Empty data URL for compatibility
        'xlink:actuate': 'onLoad',
        'xlink:show': 'other',
        'xlink:type': 'simple'
    })
    
    script = create_svg_element('script', parent=parent, **attrs)
    script.text = f"""// <![CDATA[\n{javascript}\n// ]]>"""
    return script

def pretty_print_xml(element: ET.Element) -> str:
    """Convert an XML element to a pretty-printed string.
    
    Args:
        element: The root XML element.
        
    Returns:
        Pretty-printed XML string.
    """
    # Convert to string and parse with minidom for pretty printing
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    
    # Remove extra blank lines that minidom adds
    pretty_xml = reparsed.toprettyxml(indent="  ")
    return '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
