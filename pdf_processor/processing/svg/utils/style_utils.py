""
Style-related utility functions for SVG generation.
"""
import re
from typing import Dict, List, Optional, Union, Any

def create_css_selector(selector: str, styles: Dict[str, str]) -> str:
    """Create a CSS rule with the given selector and styles.
    
    Args:
        selector: CSS selector (e.g., '.class', '#id', 'tagname').
        styles: Dictionary of CSS property-value pairs.
        
    Returns:
        A CSS rule string.
    """
    if not styles:
        return ""
    
    # Format styles as 'property: value;' pairs
    style_parts = [f"{k}: {v};" for k, v in styles.items() if v is not None]
    
    if not style_parts:
        return ""
    
    return f"{selector} {{ {' '.join(style_parts)} }}"

def merge_styles(style1: Optional[Dict[str, str]], 
                style2: Optional[Dict[str, str]]) -> Dict[str, str]:
    """Merge two style dictionaries.
    
    Args:
        style1: First style dictionary.
        style2: Second style dictionary (takes precedence).
        
    Returns:
        Merged style dictionary.
    """
    result = {}
    
    if style1:
        result.update(style1)
    if style2:
        result.update(style2)
        
    return result

def style_to_dict(style_str: str) -> Dict[str, str]:
    """Convert a CSS style string to a dictionary.
    
    Args:
        style_str: CSS style string (e.g., 'fill: red; stroke: black').
        
    Returns:
        Dictionary of style properties and values.
    """
    if not style_str:
        return {}
    
    # Split into property:value pairs and clean up
    style_dict = {}
    for prop in style_str.split(';'):
        prop = prop.strip()
        if not prop:
            continue
            
        # Split on first colon only
        if ':' in prop:
            key, value = prop.split(':', 1)
            style_dict[key.strip()] = value.strip()
    
    return style_dict

def dict_to_style(style_dict: Dict[str, str]) -> str:
    """Convert a style dictionary to a CSS style string.
    
    Args:
        style_dict: Dictionary of style properties and values.
        
    Returns:
        CSS style string.
    """
    if not style_dict:
        return ""
    
    return '; '.join(f"{k}: {v}" for k, v in style_dict.items() if v is not None)

def parse_transform(transform_str: str) -> Dict[str, List[float]]:
    """Parse an SVG transform attribute string into a dictionary of transform functions.
    
    Args:
        transform_str: The transform attribute string.
        
    Returns:
        Dictionary mapping transform functions to their arguments.
    """
    if not transform_str:
        return {}
    
    # Match transform functions like 'translate(100, 200)'
    pattern = r'([a-zA-Z]+)\(([^)]*)\)'
    transforms = {}
    
    for match in re.finditer(pattern, transform_str):
        func = match.group(1).lower()
        args_str = match.group(2).strip()
        
        # Parse arguments (can be comma or space separated)
        args = []
        for arg in re.split(r'[,\s]+', args_str):
            arg = arg.strip()
            if arg:
                try:
                    # Try to convert to float, otherwise keep as string
                    args.append(float(arg))
                except ValueError:
                    args.append(arg)
        
        transforms[func] = args
    
    return transforms

def create_transform(transforms: Dict[str, List[float]]) -> str:
    """Create an SVG transform attribute string from a dictionary of transforms.
    
    Args:
        transforms: Dictionary mapping transform functions to their arguments.
        
    Returns:
        SVG transform attribute string.
    """
    if not transforms:
        return ""
    
    transform_parts = []
    
    for func, args in transforms.items():
        if not args:
            continue
            
        # Convert arguments to strings and join with spaces
        arg_str = ' '.join(str(arg) for arg in args)
        transform_parts.append(f"{func}({arg_str})")
    
    return ' '.join(transform_parts)
