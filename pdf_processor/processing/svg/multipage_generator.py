"""
Module for generating multi-page SVG documents from multiple page images and OCR results.
"""
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
from xml.etree import ElementTree as ET
import logging

from .base_generator import SVGGenerator, SVGConfig
from pdf_processor.models.ocr_result import OCRResult

logger = logging.getLogger(__name__)

def generate_multi_page_svg(
    pages: List[Dict[str, Any]],
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[SVGConfig] = None
) -> Optional[str]:
    """Generate a multi-page SVG document with navigation controls.
    
    Args:
        pages: List of page dictionaries, each containing:
            - 'image_path': Path to the page image
            - 'ocr_result': OCRResult for the page
            - 'title': Optional page title
        output_path: Path to save the SVG file. If None, return the SVG as a string.
        config: Configuration for SVG generation.
        
    Returns:
        The SVG as a string if output_path is None, otherwise None.
    """
    generator = SVGGenerator(config or SVGConfig())
    svg_root = generator._create_multi_page_svg(pages)
    
    # Convert to string
    svg_str = generator._pretty_print(svg_root)
    
    # Save to file or return string
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_str)
        logger.info(f"Multi-page SVG saved to {output_path}")
        return None
    return svg_str

# Add the _create_multi_page_svg method to SVGGenerator
def _create_multi_page_svg(self, pages: List[Dict[str, Any]]) -> ET.Element:
    """Create an SVG element for multiple pages with navigation.
    
    Args:
        pages: List of page dictionaries with image_path, ocr_result, and optional title.
        
    Returns:
        The root SVG element.
    """
    # Calculate total dimensions
    page_heights = []
    page_widths = []
    
    for page in pages:
        img_path = page.get('image_path')
        if not img_path:
            continue
            
        width, height = self._get_image_size(img_path)
        if self.config.page_width:
            # Scale height to maintain aspect ratio
            scale = self.config.page_width / width
            height = int(height * scale)
            width = self.config.page_width
            
        page_heights.append(height)
        page_widths.append(width)
    
    if not page_heights:
        raise ValueError("No valid pages provided")
    
    # Use the widest page width
    total_width = max(page_widths) if page_widths else 800
    total_height = sum(page_heights) + (len(page_heights) - 1) * self.config.page_spacing
    
    # Add space for navigation
    nav_height = 50 if len(pages) > 1 and self.config.show_navigation else 0
    total_height += nav_height
    
    # Create SVG root element
    svg_attribs = {
        'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink',
        'width': str(total_width),
        'height': str(total_height),
        'viewBox': f'0 0 {total_width} {total_height}',
        'version': '1.1',
        'id': 'svg-root'
    }
    
    svg_root = self._create_svg_element('svg', **svg_attribs)
    
    # Add background
    bg = self._create_svg_element(
        'rect',
        width='100%',
        height='100%',
        fill=self.config.background_color
    )
    svg_root.append(bg)
    
    # Add navigation
    if len(pages) > 1 and self.config.show_navigation:
        self._add_navigation_controls(svg_root, len(pages))
    
    # Add pages
    y_offset = nav_height
    
    for i, page in enumerate(pages):
        img_path = page.get('image_path')
        ocr_result = page.get('ocr_result')
        title = page.get('title', f'Page {i+1}')
        
        if not img_path or not ocr_result:
            continue
            
        # Create page group
        page_group = self._create_svg_element(
            'g',
            id=f'page-{i}',
            class_='page',
            transform=f'translate(0, {y_offset})',
            visibility='hidden'  # Will be shown by JavaScript
        )
        
        # Get image dimensions
        img_width, img_height = self._get_image_size(img_path)
        
        # Scale if needed
        scale = 1.0
        if self.config.page_width and img_width > self.config.page_width:
            scale = self.config.page_width / img_width
            img_width = self.config.page_width
            img_height = int(img_height * scale)
        
        # Add page background
        page_bg = self._create_svg_element(
            'rect',
            x='0',
            y='0',
            width=str(img_width),
            height=str(img_height),
            fill='white',
            stroke='#ccc',
            stroke_width='1'
        )
        page_group.append(page_bg)
        
        # Add page image
        img = self._create_svg_element(
            'image',
            x='0',
            y='0',
            width=str(img_width),
            height=str(img_height),
            xlink_href=self._image_to_base64(img_path)
        )
        page_group.append(img)
        
        # Add OCR text blocks
        if hasattr(ocr_result, 'blocks') and ocr_result.blocks:
            text_group = self._create_svg_element('g', class_='text-layer')
            
            for block in ocr_result.blocks:
                # Scale block coordinates if needed
                if scale != 1.0 and hasattr(block, 'bbox'):
                    scaled_block = block.copy()
                    scaled_block.bbox = [
                        int(coord * scale) for coord in block.bbox
                    ]
                    # Scale line and word coordinates as well
                    for line in getattr(scaled_block, 'lines', []):
                        if hasattr(line, 'bbox'):
                            line.bbox = [int(coord * scale) for coord in line.bbox]
                        for word in getattr(line, 'words', []):
                            if hasattr(word, 'bbox'):
                                word.bbox = [int(coord * scale) for coord in word.bbox]
                    self._add_text_block(text_group, scaled_block)
                else:
                    self._add_text_block(text_group, block)
            
            page_group.append(text_group)
        
        # Add page title
        title_text = self._create_svg_element(
            'text',
            x='10',
            y='-10',
            font_family=self.config.font_family,
            font_size='14',
            fill='#666'
        )
        title_text.text = title
        page_group.append(title_text)
        
        svg_root.append(page_group)
        y_offset += img_height + self.config.page_spacing
    
    # Add watermark if specified
    self._add_watermark(svg_root, total_width, total_height)
    
    # Add CSS styles and JavaScript
    self._add_styles(svg_root)
    if len(pages) > 1:
        self._add_javascript(svg_root, len(pages))
    
    return svg_root

# Add the method to the SVGGenerator class
SVGGenerator._create_multi_page_svg = _create_multi_page_svg
