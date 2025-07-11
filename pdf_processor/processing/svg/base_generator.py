"""
Base SVG generator module providing core functionality for SVG generation.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union, Any
import base64
import re
import logging
from pathlib import Path
from PIL import Image
import numpy as np
from xml.etree import ElementTree as ET
from xml.dom import minidom

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class SVGConfig:
    """Configuration for SVG generation."""
    # General settings
    background_color: str = "#ffffff"
    page_width: Optional[int] = None  # If None, use original image width
    page_height: Optional[int] = None  # If None, use original image height
    
    # Text settings
    font_family: str = "Arial, sans-serif"
    font_size: int = 12
    text_color: str = "#000000"
    
    # Highlight settings
    highlight_color: str = "rgba(255, 255, 0, 0.3)"
    
    # Watermark settings
    watermark_text: Optional[str] = None
    watermark_font_size: int = 24
    watermark_color: str = "rgba(0, 0, 0, 0.1)"
    
    # Interactive elements
    show_navigation: bool = True
    show_page_numbers: bool = True
    
    # Multi-page settings
    page_spacing: int = 20
    
    # Debug settings
    show_bounding_boxes: bool = False
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.page_width is not None and self.page_width <= 0:
            raise ValueError("page_width must be positive")
        if self.page_height is not None and self.page_height <= 0:
            raise ValueError("page_height must be positive")
        if self.page_spacing < 0:
            raise ValueError("page_spacing must be non-negative")


class SVGGenerator:
    """Base class for SVG generation with common utility methods."""
    
    def __init__(self, config: Optional[SVGConfig] = None):
        """Initialize the SVG generator with the given configuration.
        
        Args:
            config: SVG configuration. If None, default values will be used.
        """
        self.config = config or SVGConfig()
        
        # Register XML namespaces
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    
    def _get_image_size(self, image_path: Union[str, Path]) -> Tuple[int, int]:
        """Get the dimensions of an image file.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            Tuple of (width, height) in pixels.
        """
        with Image.open(image_path) as img:
            return img.size
    
    def _image_to_base64(self, image_path: Union[str, Path]) -> str:
        """Convert an image to base64-encoded data URL.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            Base64-encoded data URL string.
        """
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            
        # Determine MIME type from file extension
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
        
        # Encode and return as data URL
        encoded = base64.b64encode(img_data).decode('ascii')
        return f"data:{mime_type};base64,{encoded}"
    
    def _create_svg_element(self, tag: str, **attrs) -> ET.Element:
        """Create an SVG element with the given tag and attributes.
        
        Args:
            tag: The SVG element tag name.
            **attrs: Attributes to set on the element.
            
        Returns:
            The created SVG element.
        """
        # Handle special case for xlink:href
        if 'xlink_href' in attrs:
            attrs['{http://www.w3.org/1999/xlink}href'] = attrs.pop('xlink_href')
            
        return ET.Element(tag, **{k: str(v) for k, v in attrs.items()})
    
    def _pretty_print(self, element: ET.Element) -> str:
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
    
    def _add_style(self, svg_root: ET.Element, css: str) -> None:
        """Add a style element to the SVG.
        
        Args:
            svg_root: The root SVG element.
            css: CSS content to add.
        """
        style = self._create_svg_element("style")
        style.text = f"""/* <![CDATA[ */\n{css}\n/* ]]> */"""
        svg_root.insert(0, style)
    
    def _add_script(self, svg_root: ET.Element, javascript: str) -> None:
        """Add a script element to the SVG.
        
        Args:
            svg_root: The root SVG element.
            javascript: JavaScript content to add.
        """
        script = self._create_svg_element(
            "script",
            **{
                'type': 'application/ecmascript',
                'xlink:href': 'data:,',  # Empty data URL
                'xlink:actuate': 'onLoad',
                'xlink:show': 'other',
                'xlink:type': 'simple'
            }
        )
        script.text = f"""// <![CDATA[\n{javascript}\n// ]]>"""
        svg_root.append(script)
    
    def _add_navigation_controls(self, svg_root: ET.Element, page_count: int) -> None:
        """Add navigation controls to the SVG.
        
        Args:
            svg_root: The root SVG element.
            page_count: Total number of pages.
        """
        if not self.config.show_navigation or page_count <= 1:
            return
            
        # Add navigation group
        nav_group = self._create_svg_element(
            "g",
            id="nav-controls",
            style="font-family: Arial, sans-serif; font-size: 12px;"
        )
        
        # Add previous button
        prev_btn = self._create_svg_element(
            "rect",
            x="10",
            y="10",
            width="80",
            height="30",
            rx="4",
            ry="4",
            fill="#f0f0f0",
            stroke="#ccc",
            style="cursor: pointer;"
        )
        prev_btn.set("onclick", "showPage(currentPage - 1)")
        nav_group.append(prev_btn)
        
        prev_text = self._create_svg_element(
            "text",
            x="50",
            y="30",
            text_anchor="middle",
            dominant_baseline="middle",
            fill="#333"
        )
        prev_text.text = "Previous"
        nav_group.append(prev_text)
        
        # Add next button
        next_btn = self._create_svg_element(
            "rect",
            x="100",
            y="10",
            width="80",
            height="30",
            rx="4",
            ry="4",
            fill="#f0f0f0",
            stroke="#ccc",
            style="cursor: pointer;"
        )
        next_btn.set("onclick", "showPage(currentPage + 1)")
        nav_group.append(next_btn)
        
        next_text = self._create_svg_element(
            "text",
            x="140",
            y="30",
            text_anchor="middle",
            dominant_baseline="middle",
            fill="#333"
        )
        next_text.text = "Next"
        nav_group.append(next_text)
        
        # Add page indicator
        if self.config.show_page_numbers:
            page_indicator = self._create_svg_element(
                "text",
                x="200",
                y="30",
                text_anchor="start",
                dominant_baseline="middle",
                fill="#333"
            )
            page_indicator.text = f"Page <tspan id='current-page'>1</tspan> of {page_count}"
            nav_group.append(page_indicator)
        
        # Add the navigation group to the SVG
        svg_root.append(nav_group)
    
    def _add_watermark(self, svg_root: ET.Element, width: int, height: int) -> None:
        """Add a watermark to the SVG.
        
        Args:
            svg_root: The root SVG element.
            width: Width of the SVG.
            height: Height of the SVG.
        """
        if not self.config.watermark_text:
            return
            
        watermark = self._create_svg_element(
            "text",
            x=str(width // 2),
            y=str(height // 2),
            text_anchor="middle",
            dominant_baseline="middle",
            font_size=str(self.config.watermark_font_size),
            fill=self.config.watermark_color,
            style=(
                f"font-family: Arial, sans-serif; "
                f"font-weight: bold; "
                f"opacity: 0.5; "
                f"pointer-events: none; "
                f"user-select: none;"
            ),
            transform=f"rotate(-45, {width//2}, {height//2})"
        )
        watermark.text = self.config.watermark_text
        
        # Add to a group with lower z-index
        watermark_group = self._create_svg_element("g", id="watermark")
        watermark_group.append(watermark)
        svg_root.append(watermark_group)
    
    def _add_javascript(self, svg_root: ET.Element, page_count: int) -> None:
        """Add JavaScript for interactive features.
        
        Args:
            svg_root: The root SVG element.
            page_count: Total number of pages.
        """
        if page_count <= 1:
            return
            
        js = """
        // Global variable to track current page
        var currentPage = 0;
        var totalPages = %d;
        
        // Function to show a specific page
        function showPage(pageNum) {
            // Validate page number
            if (pageNum < 0) pageNum = 0;
            if (pageNum >= totalPages) pageNum = totalPages - 1;
            
            // Hide all pages
            var pages = document.getElementsByClassName('page');
            for (var i = 0; i < pages.length; i++) {
                pages[i].setAttribute('visibility', 'hidden');
            }
            
            // Show the selected page
            var page = document.getElementById('page-' + pageNum);
            if (page) {
                page.setAttribute('visibility', 'visible');
                currentPage = pageNum;
                
                // Update page indicator
                var indicator = document.getElementById('current-page');
                if (indicator) {
                    indicator.textContent = (currentPage + 1);
                }
                
                // Scroll to the page
                page.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        }
        
        // Initialize - show first page
        document.addEventListener('DOMContentLoaded', function() {
            showPage(0);
            
            // Add keyboard navigation
            document.addEventListener('keydown', function(e) {
                switch(e.key) {
                    case 'ArrowLeft':
                        showPage(currentPage - 1);
                        break;
                    case 'ArrowRight':
                        showPage(currentPage + 1);
                        break;
                }
            });
        });
        """ % page_count
        
        self._add_script(svg_root, js)
