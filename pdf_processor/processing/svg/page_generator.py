"""
Module for generating single-page SVG documents from OCR results.
"""
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
from xml.etree import ElementTree as ET
import logging

from .base_generator import SVGGenerator, SVGConfig
from pdf_processor.models.ocr_result import OCRResult, TextBlock

logger = logging.getLogger(__name__)

def generate_svg_page(
    image_path: Union[str, Path],
    ocr_result: OCRResult,
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[SVGConfig] = None
) -> Optional[str]:
    """Generate an SVG file with OCR text overlaid on the original image.
    
    Args:
        image_path: Path to the source image.
        ocr_result: The OCR results to overlay on the image.
        output_path: Path to save the SVG file. If None, return the SVG as a string.
        config: Configuration for SVG generation.
        
    Returns:
        The SVG as a string if output_path is None, otherwise None.
    """
    generator = SVGGenerator(config or SVGConfig())
    svg_root = generator._create_svg_page(image_path, ocr_result)
    
    # Convert to string
    svg_str = generator._pretty_print(svg_root)
    
    # Save to file or return string
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_str)
        logger.info(f"SVG saved to {output_path}")
        return None
    return svg_str

# Add the _create_svg_page method to SVGGenerator
def _create_svg_page(self, image_path: Union[str, Path], ocr_result: OCRResult) -> ET.Element:
    """Create an SVG element for a single page.
    
    Args:
        image_path: Path to the source image.
        ocr_result: The OCR results to overlay on the image.
        
    Returns:
        The root SVG element.
    """
    # Get image dimensions
    img_width, img_height = self._get_image_size(image_path)
    
    # Create SVG root element with namespaces
    svg_attribs = {
        'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink',
        'width': str(self.config.page_width or img_width),
        'height': str(self.config.page_height or img_height),
        'viewBox': f'0 0 {img_width} {img_height}',
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
    
    # Add the original image
    image = self._create_svg_element(
        'image',
        x='0',
        y='0',
        width=str(img_width),
        height=str(img_height),
        xlink_href=self._image_to_base64(image_path)
    )
    svg_root.append(image)
    
    # Add OCR text blocks
    if ocr_result.blocks:
        text_group = self._create_svg_element('g', id='text-layer')
        
        for block in ocr_result.blocks:
            self._add_text_block(text_group, block)
            
        svg_root.append(text_group)
    
    # Add watermark if specified
    self._add_watermark(svg_root, img_width, img_height)
    
    # Add CSS styles
    self._add_styles(svg_root)
    
    return svg_root

def _add_text_block(self, parent: ET.Element, block: TextBlock) -> None:
    """Add a text block to the SVG.
    
    Args:
        parent: The parent SVG element.
        block: The text block to add.
    """
    # Create a group for the text block
    group = self._create_svg_element(
        'g',
        class_='text-block',
        **block.metadata.get('svg_attrs', {})
    )
    
    # Add bounding box if enabled
    if self.config.show_bounding_boxes and hasattr(block, 'bbox'):
        bbox = block.bbox
        rect = self._create_svg_element(
            'rect',
            x=str(bbox[0]),
            y=str(bbox[1]),
            width=str(bbox[2] - bbox[0]),
            height=str(bbox[3] - bbox[1]),
            fill='none',
            stroke='red',
            stroke_width='1',
            opacity='0.5'
        )
        group.append(rect)
    
    # Add text elements
    for line in block.lines:
        text = self._create_svg_element(
            'text',
            x=str(line.bbox[0]),
            y=str(line.bbox[3]),  # Baseline at bottom of bbox
            font_family=self.config.font_family,
            font_size=str(self.config.font_size),
            fill=self.config.text_color,
            style='white-space: pre;'
        )
        
        # Add text content with proper positioning for each word
        text_content = []
        x_pos = line.bbox[0]
        
        for word in line.words:
            word_text = word.text + ' '
            tspan = ET.SubElement(text, 'tspan', {
                'x': str(word.bbox[0]),
                'y': str(word.bbox[3]),
                'data-text': word_text.strip()
            })
            tspan.text = word_text
        
        group.append(text)
    
    parent.append(group)

def _add_styles(self, svg_root: ET.Element) -> None:
    """Add CSS styles to the SVG.
    
    Args:
        svg_root: The root SVG element.
    """
    css = """
    .text-block {
        cursor: text;
        user-select: text;
    }
    
    .text-block text {
        fill: %s;
        font-family: %s;
        font-size: %dpx;
        pointer-events: none;
    }
    
    .text-block text::selection {
        fill: #000000;
        background-color: %s;
    }
    
    .highlight {
        fill: %s;
        opacity: 0.3;
    }
    """ % (
        self.config.text_color,
        self.config.font_family,
        self.config.font_size,
        self.config.highlight_color,
        self.config.highlight_color
    )
    
    self._add_style(svg_root, css)

# Add the methods to the SVGGenerator class
SVGGenerator._create_svg_page = _create_svg_page
SVGGenerator._add_text_block = _add_text_block
SVGGenerator._add_styles = _add_styles
