""
SVG image element generators.
"""
import base64
from pathlib import Path
from typing import Dict, Optional, Tuple, Union, Any
from xml.etree import ElementTree as ET

def create_image_element(
    image_path: Union[str, Path],
    x: Union[int, float, str] = 0,
    y: Union[int, float, str] = 0,
    width: Optional[Union[int, float, str]] = None,
    height: Optional[Union[int, float, str]] = None,
    preserve_aspect_ratio: str = "xMidYMid meet",
    **attrs
) -> ET.Element:
    """Create an SVG image element from an image file.
    
    Args:
        image_path: Path to the image file.
        x: X coordinate of the top-left corner.
        y: Y coordinate of the top-left corner.
        width: Width of the image. If None, uses the image's natural width.
        height: Height of the image. If None, uses the image's natural height.
        preserve_aspect_ratio: How to handle aspect ratio (see SVG spec).
        **attrs: Additional SVG attributes.
        
    Returns:
        An SVG image element.
    """
    # Read image data and get dimensions
    with open(image_path, "rb") as img_file:
        img_data = img_file.read()
    
    # Get MIME type from file extension
    ext = Path(image_path).suffix.lower()
    mime_type = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.webp': 'image/webp'
    }.get(ext, 'application/octet-stream')
    
    # Encode image data as base64
    encoded = base64.b64encode(img_data).decode('ascii')
    href = f"data:{mime_type};base64,{encoded}"
    
    # Create attributes dictionary
    img_attrs = {
        'x': str(x),
        'y': str(y),
        'preserveAspectRatio': preserve_aspect_ratio,
        'xlink:href': href
    }
    
    # Add width and height if provided
    if width is not None:
        img_attrs['width'] = str(width)
    if height is not None:
        img_attrs['height'] = str(height)
    
    # Add any additional attributes
    img_attrs.update(attrs)
    
    return ET.Element('image', img_attrs)

def create_embedded_image(
    image_data: bytes,
    mime_type: str,
    x: Union[int, float, str] = 0,
    y: Union[int, float, str] = 0,
    width: Optional[Union[int, float, str]] = None,
    height: Optional[Union[int, float, str]] = None,
    **attrs
) -> ET.Element:
    """Create an SVG image element from binary image data.
    
    Args:
        image_data: Binary image data.
        mime_type: MIME type of the image (e.g., 'image/png', 'image/jpeg').
        x: X coordinate of the top-left corner.
        y: Y coordinate of the top-left corner.
        width: Width of the image.
        height: Height of the image.
        **attrs: Additional SVG attributes.
        
    Returns:
        An SVG image element.
    """
    # Encode image data as base64
    encoded = base64.b64encode(image_data).decode('ascii')
    href = f"data:{mime_type};base64,{encoded}"
    
    # Create attributes dictionary
    img_attrs = {
        'x': str(x),
        'y': str(y),
        'xlink:href': href
    }
    
    # Add width and height if provided
    if width is not None:
        img_attrs['width'] = str(width)
    if height is not None:
        img_attrs['height'] = str(height)
    
    # Add any additional attributes
    img_attrs.update(attrs)
    
    return ET.Element('image', img_attrs)
