"""Image enhancement utilities for OCR preprocessing."""

from typing import Optional, Dict, Any, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import cv2

from ..models.retry_config import RetryConfig
from ..utils.validation_utils import validate_image_file, validate_positive_number
from ..utils.logging_utils import setup_logger


class EnhancementStrategy(Enum):
    """Available image enhancement strategies."""
    ORIGINAL = auto()
    GRAYSCALE = auto()
    ADAPTIVE_THRESHOLD = auto()
    CONTRAST_STRETCH = auto()
    SHARPEN = auto()
    DENOISE = auto()
    BINARIZATION = auto()
    DESKEW = auto()


@dataclass
class EnhancementResult:
    """Result of an image enhancement operation."""
    image: Image.Image
    strategy: EnhancementStrategy
    parameters: Dict[str, Any]
    success: bool = True
    error: Optional[str] = None


class ImageEnhancer:
    """Handles various image enhancement techniques for OCR preprocessing."""
    
    def __init__(self, default_strategies: Optional[List[EnhancementStrategy]] = None):
        """Initialize the image enhancer.
        
        Args:
            default_strategies: List of enhancement strategies to apply by default
        """
        self.logger = setup_logger('image_enhancer')
        self.default_strategies = default_strategies or [
            EnhancementStrategy.ORIGINAL,
            EnhancementStrategy.GRAYSCALE,
            EnhancementStrategy.ADAPTIVE_THRESHOLD,
            EnhancementStrategy.CONTRAST_STRETCH
        ]
        self.retry_config = RetryConfig(
            max_retries=2,
            initial_delay=0.1,
            max_delay=1.0
        )
    
    def enhance_image(
        self, 
        image_path: str,
        strategies: Optional[List[EnhancementStrategy]] = None,
        **kwargs
    ) -> List[EnhancementResult]:
        """Apply enhancement strategies to an image.
        
        Args:
            image_path: Path to the input image
            strategies: List of enhancement strategies to apply
            **kwargs: Additional parameters for enhancement methods
            
        Returns:
            List of EnhancementResult objects, one for each strategy
        """
        try:
            # Validate input
            image_path = validate_image_file(image_path)
            strategies = strategies or self.default_strategies
            
            # Load the original image
            with Image.open(image_path) as img:
                original_image = img.convert('RGB')
            
            results = []
            
            # Apply each strategy
            for strategy in strategies:
                result = self._apply_enhancement_strategy(original_image, strategy, **kwargs)
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error enhancing image {image_path}: {e}", exc_info=True)
            raise
    
    def _apply_enhancement_strategy(
        self,
        image: Image.Image,
        strategy: EnhancementStrategy,
        **kwargs
    ) -> EnhancementResult:
        """Apply a single enhancement strategy to an image.
        
        Args:
            image: Input PIL Image
            strategy: Enhancement strategy to apply
            **kwargs: Strategy-specific parameters
            
        Returns:
            EnhancementResult with the enhanced image
        """
        method_name = f"_enhance_{strategy.name.lower()}"
        if not hasattr(self, method_name):
            return EnhancementResult(
                image=image,
                strategy=strategy,
                parameters={},
                success=False,
                error=f"Unsupported enhancement strategy: {strategy}"
            )
        
        try:
            method = getattr(self, method_name)
            enhanced_image = method(image.copy(), **kwargs)
            
            return EnhancementResult(
                image=enhanced_image,
                strategy=strategy,
                parameters=kwargs,
                success=True
            )
            
        except Exception as e:
            self.logger.warning(
                f"Failed to apply {strategy}: {e}",
                extra={"strategy": strategy.name, "error": str(e)}
            )
            return EnhancementResult(
                image=image,
                strategy=strategy,
                parameters=kwargs,
                success=False,
                error=str(e)
            )
    
    # --- Enhancement Methods ---
    
    def _enhance_original(self, image: Image.Image, **kwargs) -> Image.Image:
        """Return the original image (no enhancement)."""
        return image
    
    def _enhance_grayscale(self, image: Image.Image, **kwargs) -> Image.Image:
        """Convert image to grayscale."""
        if image.mode != 'L':
            return image.convert('L')
        return image
    
    def _enhance_adaptive_threshold(
        self, 
        image: Image.Image,
        block_size: int = 11,
        c: int = 2,
        **kwargs
    ) -> Image.Image:
        """Apply adaptive thresholding to the image."""
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Convert to numpy array for OpenCV
        img_array = np.array(image)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            img_array, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            c
        )
        
        # Convert back to PIL Image
        return Image.fromarray(thresh)
    
    def _enhance_contrast_stretch(
        self, 
        image: Image.Image,
        low: float = 2.0,
        high: float = 98.0,
        **kwargs
    ) -> Image.Image:
        """Stretch the contrast of the image using histogram equalization."""
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Calculate percentiles
        plow, phigh = np.percentile(img_array, (low, high))
        
        # Apply contrast stretching
        img_stretched = np.clip((img_array - plow) * (255.0 / (phigh - plow)), 0, 255).astype(np.uint8)
        
        return Image.fromarray(img_stretched)
    
    def _enhance_sharpen(
        self, 
        image: Image.Image,
        factor: float = 2.0,
        **kwargs
    ) -> Image.Image:
        """Sharpen the image."""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    
    def _enhance_denoise(
        self,
        image: Image.Image,
        h: float = 10.0,
        h_color: float = 10.0,
        template_window_size: int = 7,
        search_window_size: int = 21,
        **kwargs
    ) -> Image.Image:
        """Remove noise from the image using non-local means denoising."""
        # Convert to BGR for OpenCV
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        img_array = np.array(image)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoisingColored(
            img_bgr,
            None,
            h,
            h_color,
            templateWindowSize=template_window_size,
            searchWindowSize=search_window_size
        )
        
        # Convert back to RGB
        denoised_rgb = cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB)
        return Image.fromarray(denoised_rgb)
    
    def _enhance_binarization(
        self,
        image: Image.Image,
        threshold: int = 200,
        **kwargs
    ) -> Image.Image:
        """Convert image to black and white using a threshold."""
        if image.mode != 'L':
            image = image.convert('L')
        return image.point(lambda p: 255 if p > threshold else 0)
    
    def _enhance_deskew(
        self,
        image: Image.Image,
        **kwargs
    ) -> Image.Image:
        """Deskew the image by detecting and correcting skew angle."""
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Convert to numpy array for OpenCV
        img_array = np.array(image)
        
        # Threshold the image
        _, thresh = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find coordinates of non-zero pixels
        coords = np.column_stack(np.where(thresh > 0))
        
        # Get minimum area rectangle
        angle = cv2.minAreaRect(coords)[-1]
        
        # Adjust angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Rotate the image
        (h, w) = img_array.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            img_array, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return Image.fromarray(rotated)
