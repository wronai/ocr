"""Data models for OCR results."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class TextBlock:
    """Represents a block of text with its position and confidence."""
    text: str
    x: float
    y: float
    width: float
    height: float
    confidence: float = 1.0
    language: str = "pl"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OCRResult:
    """Container for OCR processing results."""
    text: str = ""
    blocks: List[TextBlock] = field(default_factory=list)
    language: str = "pl"
    confidence: float = 0.0
    model: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary."""
        result = asdict(self)
        result["blocks"] = [asdict(block) for block in self.blocks]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OCRResult':
        """Create an OCRResult from a dictionary."""
        blocks_data = data.pop("blocks", [])
        result = cls(**data)
        result.blocks = [TextBlock(**block) for block in blocks_data]
        return result
    
    def add_block(self, text: str, x: float, y: float, width: float, height: float, 
                 confidence: float = 1.0, **metadata) -> None:
        """Add a text block to the result."""
        self.blocks.append(TextBlock(
            text=text,
            x=x,
            y=y,
            width=width,
            height=height,
            confidence=confidence,
            metadata=metadata or {}
        ))
        self.text += f"\n{text}" if self.text else text
    
    def calculate_confidence(self) -> float:
        """Calculate the average confidence of all text blocks."""
        if not self.blocks:
            return 0.0
        return sum(block.confidence for block in self.blocks) / len(self.blocks)
    
    def filter_by_confidence(self, min_confidence: float) -> 'OCRResult':
        """Return a new OCRResult with blocks above the minimum confidence."""
        filtered = OCRResult(
            language=self.language,
            model=self.model,
            metadata=self.metadata.copy()
        )
        
        for block in self.blocks:
            if block.confidence >= min_confidence:
                filtered.blocks.append(block)
                filtered.text += f"\n{block.text}" if filtered.text else block.text
        
        filtered.confidence = filtered.calculate_confidence()
        return filtered
