"""
Data models for OCR processing.

This module provides data structures for representing OCR results and related entities.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Re-export the existing models for backward compatibility
from ...models.ocr_result import OCRResult, TextBlock

# Add any additional OCR-specific models below

@dataclass
class BoundingBox:
    """Represents a bounding box with coordinates and dimensions."""
    x: float
    y: float
    width: float
    height: float
    
    def to_tuple(self) -> Tuple[float, float, float, float]:
        """Convert to (x, y, width, height) tuple."""
        return (self.x, self.y, self.width, self.height)
    
    @classmethod
    def from_xyxy(cls, x1: float, y1: float, x2: float, y2: float) -> 'BoundingBox':
        """Create from (x1, y1, x2, y2) coordinates."""
        return cls(
            x=x1,
            y=y1,
            width=x2 - x1,
            height=y2 - y1
        )
    
    @property
    def area(self) -> float:
        """Calculate the area of the bounding box."""
        return self.width * self.height
    
    def intersection(self, other: 'BoundingBox') -> float:
        """Calculate intersection area with another bounding box."""
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.x + self.width, other.x + other.width)
        y2 = min(self.y + self.height, other.y + other.height)
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
            
        return (x2 - x1) * (y2 - y1)
    
    def iou(self, other: 'BoundingBox') -> float:
        """Calculate Intersection over Union (IoU) with another bounding box."""
        intersection = self.intersection(other)
        union = self.area + other.area - intersection
        
        if union == 0:
            return 0.0
            
        return intersection / union
