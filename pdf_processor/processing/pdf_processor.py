"""Main PDF processing module for OCR."""

import os
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable

import fitz  # PyMuPDF
from PIL import Image
import numpy as np

from ..models.ocr_result import OCRResult
from ..models.retry_config import RetryConfig
from ..utils.file_utils import (
    ensure_directory_exists,
    create_temp_file,
    cleanup_temp_files,
    pdf_to_images,
    save_image
)
from ..utils.logging_utils import setup_logger, log_execution_time
from ..utils.validation_utils import validate_positive_number, validate_pdf_file
from .image_enhancement import ImageEnhancer, EnhancementStrategy
from .ocr_processor import OCRProcessor
from .svg.base_generator import SVGGenerator, SVGConfig


@dataclass
class PDFProcessorConfig:
    """Configuration for the PDF processor."""
    # Input/Output
    input_path: Union[str, Path]
    output_dir: Union[str, Path]
    
    # Processing
    ocr_model: str = "llava:7b"
    language: str = "polish"
    dpi: int = 300
    max_workers: int = 4
    timeout: int = 300  # seconds
    
    # Image enhancement
    enhancement_strategies: List[EnhancementStrategy] = field(
        default_factory=lambda: [
            EnhancementStrategy.ORIGINAL,
            EnhancementStrategy.GRAYSCALE,
            EnhancementStrategy.ADAPTIVE_THRESHOLD,
        ]
    )
    
    # Output options
    save_images: bool = True
    save_svg: bool = True
    save_text: bool = True
    
    # Multi-page SVG options
    combine_pages: bool = True  # Whether to combine all pages into a single SVG
    page_spacing: int = 20      # Space between pages in the combined SVG (pixels)
    
    # Retry configuration
    max_retries: int = 3
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Union[str, Path]] = None
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Convert paths to Path objects
        self.input_path = Path(self.input_path).expanduser().resolve()
        self.output_dir = Path(self.output_dir).expanduser().resolve()
        
        # Validate values
        self.dpi = max(72, min(600, self.dpi))  # Clamp between 72-600 DPI
        self.max_workers = max(1, min(os.cpu_count() or 1, self.max_workers))
        self.timeout = max(30, self.timeout)  # Minimum 30 seconds
        self.max_retries = max(0, self.max_retries)
        self.page_spacing = max(0, self.page_spacing)  # Ensure non-negative
        
        # Ensure output directory exists
        ensure_directory_exists(self.output_dir)


class PDFProcessor:
    """Main class for processing PDFs with OCR."""
    
    def __init__(self, config: Optional[PDFProcessorConfig] = None):
        """Initialize the PDF processor.
        
        Args:
            config: Configuration for the processor
        """
        self.config = config or PDFProcessorConfig(
            input_path=".",
            output_dir="./output"
        )
        
        # Set up logging
        self.logger = setup_logger(
            'pdf_processor',
            log_level=self.config.log_level,
            log_file=self.config.log_file
        )
        
        # Initialize components
        self.image_enhancer = ImageEnhancer(
            default_strategies=self.config.enhancement_strategies
        )
        
        self.ocr_processor = OCRProcessor(
            model=self.config.ocr_model,
            timeout=self.config.timeout,
            retry_config=RetryConfig(
                max_retries=self.config.max_retries,
                initial_delay=2.0,
                max_delay=30.0
            )
        )
        
        self.svg_generator = SVGGenerator()
        
        # Track processed files and statistics
        self.processed_files: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
    
    @log_execution_time(setup_logger('pdf_processor'))
    def process_pdf(
        self,
        pdf_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """Process a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Output directory (overrides config if provided)
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        pdf_path = Path(pdf_path).expanduser().resolve()
        output_dir = Path(output_dir) if output_dir else self.config.output_dir
        
        result = {
            'pdf_path': str(pdf_path),
            'status': 'started',
            'start_time': datetime.now().isoformat(),
            'pages_processed': 0,
            'total_pages': 0,
            'output_files': [],
            'errors': []
        }
        
        try:
            self.logger.info(f"Processing PDF: {pdf_path.name}")
            
            # Create output directory for this PDF
            pdf_output_dir = output_dir / pdf_path.stem
            ensure_directory_exists(pdf_output_dir)
            
            # Convert PDF to images
            self.logger.debug(f"Converting PDF to images (DPI: {self.config.dpi})")
            image_paths = pdf_to_images(pdf_path, dpi=self.config.dpi)
            result['total_pages'] = len(image_paths)
            
            if not image_paths:
                raise ValueError("No pages found in PDF")
            
            # Process each page
            page_results = []
            for i, image_path in enumerate(image_paths, 1):
                try:
                    page_result = self._process_page(
                        image_path=image_path,
                        page_num=i,
                        output_dir=pdf_output_dir
                    )
                    page_results.append(page_result)
                    result['pages_processed'] += 1
                    
                except Exception as e:
                    error_msg = f"Error processing page {i}: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    result['errors'].append({
                        'page': i,
                        'error': str(e),
                        'type': type(e).__name__
                    })
            
            # Generate combined results if we have multiple pages
            if len(page_results) > 1:
                # Save combined text
                combined_text = "\n\n".join(
                    pr.get('text', '') for pr in page_results if pr.get('text')
                )
                
                if combined_text.strip():
                    text_output_path = pdf_output_dir / f"{pdf_path.stem}_combined.txt"
                    with open(text_output_path, 'w', encoding='utf-8') as f:
                        f.write(combined_text)
                    
                    result['output_files'].append({
                        'type': 'combined_text',
                        'path': str(text_output_path)
                    })
                
                # Generate combined SVG if enabled
                if self.config.combine_pages and self.config.save_svg:
                    svg_output_path = pdf_output_dir / f"{pdf_path.stem}_combined.svg"
                    self._generate_multi_page_svg(
                        page_results=page_results,
                        output_path=svg_output_path,
                        title=pdf_path.stem
                    )
                    
                    result['output_files'].append({
                        'type': 'combined_svg',
                        'path': str(svg_output_path)
                    })
            
            # Update result
            result.update({
                'status': 'completed',
                'end_time': datetime.now().isoformat(),
                'processing_time': time.time() - start_time,
                'output_dir': str(pdf_output_dir)
            })
            
            self.logger.info(
                f"Completed processing {pdf_path.name} "
                f"({result['pages_processed']}/{result['total_pages']} pages)"
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to process {pdf_path.name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            result.update({
                'status': 'failed',
                'end_time': datetime.now().isoformat(),
                'processing_time': time.time() - start_time,
                'error': str(e),
                'error_type': type(e).__name__
            })
            
            return result
        
        finally:
            # Clean up temporary files
            if 'image_paths' in locals():
                cleanup_temp_files(image_paths)
    
    def _process_page(
        self,
        image_path: Union[str, Path],
        page_num: int,
        output_dir: Union[str, Path]
    ) -> Dict[str, Any]:
        """Process a single page from the PDF.
        
        Args:
            image_path: Path to the page image
            page_num: Page number (1-based)
            output_dir: Directory to save output files
            
        Returns:
            Dictionary with processing results for the page
        """
        output_dir = Path(output_dir)
        page_prefix = f"page_{page_num:03d}"
        result = {
            'page': page_num,
            'image_path': str(image_path),
            'output_files': []
        }
        
        try:
            # Enhance the image using different strategies
            enhancement_results = self.image_enhancer.enhance_image(image_path)
            
            # Process each enhanced version
            ocr_results = []
            for enh_result in enhancement_results:
                if not enh_result.success:
                    self.logger.warning(
                        f"Skipping failed enhancement: {enh_result.strategy.name}"
                    )
                    continue
                
                # Save enhanced image if requested
                if self.config.save_images:
                    enh_image_path = output_dir / f"{page_prefix}_{enh_result.strategy.name.lower()}.png"
                    enh_result.image.save(enh_image_path, 'PNG')
                    
                    result['output_files'].append({
                        'type': 'enhanced_image',
                        'strategy': enh_result.strategy.name,
                        'path': str(enh_image_path)
                    })
                
                # Run OCR on the enhanced image
                ocr_result = self.ocr_processor.extract_text(
                    image_path=enh_image_path if self.config.save_images else enh_result.image,
                    language=self.config.language
                )
                
                # Add enhancement info to the result
                ocr_result.metadata.update({
                    'enhancement_strategy': enh_result.strategy.name,
                    'enhancement_params': enh_result.parameters
                })
                
                ocr_results.append(ocr_result)
            
            if not ocr_results:
                raise ValueError("No successful OCR results from any enhancement strategy")
            
            # For now, just use the first successful result
            # TODO: Implement result merging/selection logic
            best_result = ocr_results[0]
            result['text'] = best_result.text
            result['confidence'] = best_result.confidence
            
            # Store the best result and image path for multi-page SVG
            result['ocr_result'] = best_result
            result['original_image_path'] = str(image_path)
            
            # Save text output if requested
            if self.config.save_text and best_result.text.strip():
                text_output_path = output_dir / f"{page_prefix}.txt"
                with open(text_output_path, 'w', encoding='utf-8') as f:
                    f.write(best_result.text)
                
                result['output_files'].append({
                    'type': 'text',
                    'path': str(text_output_path)
                })
            
            # Generate and save SVG if requested
            if self.config.save_svg:
                svg_output_path = output_dir / f"{page_prefix}.svg"
                
                self.svg_generator.generate_svg(
                    image_path=image_path,
                    ocr_result=best_result,
                    output_path=svg_output_path,
                    page_width=best_result.metadata.get('original_width'),
                    page_height=best_result.metadata.get('original_height')
                )
                
                result['output_files'].append({
                    'type': 'svg',
                    'path': str(svg_output_path)
                })
            
            return result
            
        except Exception as e:
            self.logger.error(
                f"Error processing page {page_num}: {str(e)}",
                exc_info=True
            )
            raise
    
    def _generate_multi_page_svg(
        self,
        page_results: List[Dict[str, Any]],
        output_path: Union[str, Path],
        title: str = "Document"
    ) -> None:
        """Generate a single SVG containing multiple pages with navigation.
        
        Args:
            page_results: List of page results from _process_page
            output_path: Path to save the combined SVG
            title: Document title for the SVG
        """
        pages = []
        
        for page_result in page_results:
            if 'ocr_result' not in page_result or 'original_image_path' not in page_result:
                continue
                
            pages.append({
                'image_path': page_result['original_image_path'],
                'ocr_result': page_result['ocr_result'],
                'title': f"Page {page_result.get('page', len(pages) + 1)}"
            })
        
        if not pages:
            self.logger.warning("No valid pages found for multi-page SVG")
            return
        
        # Generate the multi-page SVG
        self.svg_generator.generate_multi_page_svg(
            pages=pages,
            output_path=output_path,
            page_width=self.config.page_width,
            page_spacing=self.config.page_spacing,
            title=title
        )
    
    def cleanup_resources(self):
        """Clean up resources used by the processor."""
        if hasattr(self, 'image_enhancer') and hasattr(self.image_enhancer, 'cleanup_resources'):
            self.image_enhancer.cleanup_resources()
        if hasattr(self, 'ocr_processor') and hasattr(self.ocr_processor, 'cleanup_resources'):
            self.ocr_processor.cleanup_resources()
        if hasattr(self, 'svg_generator') and hasattr(self.svg_generator, 'cleanup_resources'):
            self.svg_generator.cleanup_resources()
    
    def process_directory(
        self,
        input_dir: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        pattern: str = "*.pdf"
    ) -> List[Dict[str, Any]]:
        """Process all PDFs in a directory.
        
        Args:
            input_dir: Directory containing PDFs (overrides config if provided)
            output_dir: Output directory (overrides config if provided)
            pattern: File pattern to match PDFs (e.g., "*.pdf")
            
        Returns:
            List of processing results for each PDF
        """
        input_dir = Path(input_dir) if input_dir else self.config.input_path
        output_dir = Path(output_dir) if output_dir else self.config.output_dir
        
        if not input_dir.is_dir():
            raise NotADirectoryError(f"Input directory not found: {input_dir}")
        
        # Find all matching PDFs
        pdf_paths = list(input_dir.glob(pattern))
        if not pdf_paths:
            self.logger.warning(f"No PDFs found matching pattern: {pattern}")
            return []
        
        self.logger.info(f"Found {len(pdf_paths)} PDFs to process in {input_dir}")
        
        # Process each PDF
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_pdf = {
                executor.submit(self.process_pdf, pdf_path, output_dir): pdf_path
                for pdf_path in pdf_paths
            }
            
            # Process results as they complete
            for future in as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Log completion
                    status = result.get('status', 'unknown')
                    pages = f"{result.get('pages_processed', 0)}/{result.get('total_pages', 0)}"
                    self.logger.info(
                        f"{status.upper()} - {pdf_path.name} "
                        f"(Pages: {pages}, Time: {result.get('processing_time', 0):.1f}s)"
                    )
                    
                except Exception as e:
                    error_msg = f"Error processing {pdf_path.name}: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    
                    results.append({
                        'pdf_path': str(pdf_path),
                        'status': 'failed',
                        'error': str(e),
                        'error_type': type(e).__name__
                    })
        
        return results
