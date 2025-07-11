"""OCR processing using Ollama models."""

import json
import logging
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import numpy as np
from PIL import Image

from ..config.settings import (
    DEFAULT_OCR_MODEL,
    DEFAULT_TIMEOUT,
    OCR_CONFIDENCE_THRESHOLD,
)
from ..models.ocr_result import OCRResult, TextBlock
from ..models.retry_config import RetryConfig
from ..utils.logging_utils import log_execution_time, setup_logger
from ..utils.validation_utils import validate_image_file, validate_positive_number


class OCRProcessor:
    """Handles OCR processing using Ollama models."""
    
    def __init__(
        self,
        model: str = DEFAULT_OCR_MODEL,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: Optional[RetryConfig] = None
    ) -> None:
        """Initialize the OCR processor.
        
        Args:
            model: Name of the Ollama model to use for OCR
            timeout: Timeout in seconds for OCR operations
            retry_config: Configuration for retrying failed operations
        """
        self.logger = setup_logger('ocr_processor')
        self.model = model
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()
        
        # Check if Ollama is available
        self._check_ollama_available()
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is installed and the specified model is available."""
        try:
            # Check if ollama command exists
            subprocess.run(
                ['ollama', '--version'],
                capture_output=True,
                check=True,
                timeout=5
            )
            
            # Check if the model is available
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.logger.error("Failed to list Ollama models")
                return False
                
            # Check if the model is in the list
            available_models = [
                line.split()[0].split(':')[0]  # Extract model name
                for line in result.stdout.splitlines()[1:]  # Skip header
                if line.strip()
            ]
            
            model_base = self.model.split(':')[0]  # Remove tag if present
            if model_base not in available_models:
                self.logger.warning(
                    f"Model {self.model} is not available. "
                    f"Available models: {', '.join(available_models)}"
                )
                return False
                
            return True
            
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            self.logger.error(f"Ollama is not available: {e}")
            return False
    
    @log_execution_time(setup_logger('ocr_processor'))
    def _call_ollama_ocr(
        self,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
        language: str = "polish"
    ) -> Dict[str, Any]:
        """Call the Ollama API to perform OCR on an image.
        
        Args:
            image_path: Path to the image file
            prompt: Custom prompt to use for the OCR model
            language: Language of the text in the image
            
        Returns:
            Dictionary containing the OCR results
            
        Raises:
            RuntimeError: If the Ollama command fails
            ValueError: If the output cannot be parsed
            TimeoutError: If the operation times out
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Use the default prompt if none provided
        if prompt is None:
            prompt = (
                f"Extract all text from this image in {language} with high accuracy. "
                "Return a JSON object with the following structure: "
                '{"text": "full text", '  
                '"blocks": [{"text": "text", "x": 0, "y": 0, '
                '"width": 0, "height": 0, "confidence": 0.95}]} ' 
                'where x,y,width,height are the bounding box coordinates ' 
                'and confidence is between 0 and 1. '
                'Return ONLY the JSON object, no other text.'
            )
        
        # Build the command
        cmd = ['ollama', 'run', self.model, prompt]
        
        # Add the image as input
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
        except Exception as e:
            self.logger.error(f"Failed to read image file {image_path}: {e}")
            raise RuntimeError(f"Failed to read image file: {e}")
        
        self.logger.info(
            f"Starting OCR processing for {image_path.name} with timeout={self.timeout}s"
        )
        start_time = time.time()
        
        try:
            # Run the command with a timeout
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                input=image_data,
                capture_output=True,
                timeout=self.timeout,
                check=False  # We'll handle non-zero return codes ourselves
            )
            
            processing_time = time.time() - start_time
            self.logger.info(f"OCR processing completed in {processing_time:.2f} seconds")
            
            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='replace')
                self.logger.error(
                    f"Ollama command failed with code {result.returncode}: {error_msg}"
                )
                raise RuntimeError(
                    f"Ollama error (code {result.returncode}): {error_msg}"
                )
            
            # Parse the output
            output = result.stdout.decode('utf-8', errors='replace').strip()
            if not output:
                self.logger.error("Empty response received from Ollama")
                raise ValueError("Empty response from Ollama")
            
            # Log a sample of the output for debugging
            self.logger.debug(f"Raw OCR output (first 200 chars): {output[:200]}...")
            
            # Parse the OCR result
            try:
                ocr_result = self._parse_ollama_output(output, language)
                if not ocr_result.text.strip() and not ocr_result.blocks:
                    self.logger.warning("OCR succeeded but returned no text or blocks")
                self.logger.info(
                    f"Successfully parsed OCR result with {len(ocr_result.blocks)} "
                    f"text blocks and {len(ocr_result.text)} characters of text"
                )
                # Convert OCRResult to dict before returning
                return ocr_result.to_dict()
                
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.error(f"Failed to parse Ollama output as JSON: {e}")
                # Try to extract JSON from the output in case there's extra text
                try:
                    json_str = self._extract_json(output)
                    if json_str:
                        self.logger.info("Extracted JSON from output, attempting to parse...")
                        ocr_result = json.loads(json_str)
                        self.logger.info("Successfully parsed extracted JSON")
                        return ocr_result
                except Exception as parse_error:
                    self.logger.error(f"Failed to extract/parse JSON from output: {parse_error}")
                
                self.logger.debug(f"Raw output (first 500 chars): {output[:500]}...")
                raise ValueError(
                    f"Failed to parse Ollama output as JSON: {e}"
                )
            
        except subprocess.TimeoutExpired as e:
            processing_time = time.time() - start_time
            self.logger.error(
                f"Ollama command timed out after {processing_time:.1f} seconds. "
                f"Consider using a faster model or increasing the timeout (current: {self.timeout}s)."
            )
            # Try to get any partial output
            if hasattr(e, 'stdout') and e.stdout:
                partial_output = e.stdout.decode('utf-8', errors='replace').strip()
                if partial_output:
                    self.logger.debug(f"Partial output before timeout: {partial_output[:500]}...")
            raise TimeoutError(
                f"Ollama command timed out after {processing_time:.1f} seconds"
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(
                f"Unexpected error during OCR processing after {processing_time:.1f} seconds: {str(e)}",
                exc_info=True
            )
            raise
    
    @log_execution_time(setup_logger('ocr_processor'))
    def extract_text(
        self,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
        language: str = "polish",
        **kwargs
    ) -> OCRResult:
        """Extract text from an image using the configured OCR model.
        
        Args:
            image_path: Path to the input image
            prompt: Custom prompt to use for the OCR model
            language: Language of the text in the image
            **kwargs: Additional parameters for the OCR model
            
        Returns:
            OCRResult containing the extracted text and metadata
            
        Raises:
            RuntimeError: If OCR processing fails
            FileNotFoundError: If the image file does not exist
        """
        # Validate input
        image_path = validate_image_file(image_path)
        
        # Prepare the prompt
        if prompt is None:
            prompt = self._get_default_prompt(language)
        
        last_error = None
        
        # Try multiple times if needed
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Call the Ollama API and get the OCR result as a dictionary
                ocr_dict = self._call_ollama_ocr(image_path, prompt, language)
                
                # Convert the dictionary to an OCRResult object
                ocr_result = OCRResult(
                    text=ocr_dict.get('text', ''),
                    language=language,
                    confidence=float(ocr_dict.get('confidence', 0.0)),
                    model=self.model,
                    metadata={
                        'model': self.model,
                        'image_path': str(image_path),
                        'attempt': attempt + 1,
                        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                        **ocr_dict.get('metadata', {})  # Include any metadata from the OCR result
                    }
                )
                
                # Add text blocks if available
                if 'blocks' in ocr_dict and isinstance(ocr_dict['blocks'], list):
                    for block_data in ocr_dict['blocks']:
                        ocr_result.blocks.append(TextBlock(
                            text=block_data.get('text', ''),
                            x=float(block_data.get('x', 0)),
                            y=float(block_data.get('y', 0)),
                            width=float(block_data.get('width', 0)),
                            height=float(block_data.get('height', 0)),
                            confidence=float(block_data.get('confidence', 0.95)),
                            language=block_data.get('language', language),
                            metadata=block_data.get('metadata', {})
                        ))
                
                return ocr_result
                
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {e}",
                    extra={'attempt': attempt + 1, 'error': str(e)}
                )
    
    @log_execution_time(setup_logger('ocr_processor'))
    def extract_text(
        self,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
        language: str = "polish"
    ) -> Dict[str, Any]:
        """Extract text from an image using the configured OCR model.
        
        Args:
            image_path: Path to the image file
            prompt: Custom prompt to use for the OCR model
            language: Language of the text in the image
            
        Returns:
            Dictionary containing the OCR results
            
        Raises:
            RuntimeError: If the Ollama command fails
            ValueError: If the output cannot be parsed
            TimeoutError: If the operation times out
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Use the default prompt if none provided
        if prompt is None:
            prompt = (
                f"Extract all text from this image in {language} with high accuracy. "
                "Return a JSON object with the following structure: "
                '{"text": "full text", '  
                '"blocks": [{"text": "text", "x": 0, "y": 0, '
                '"width": 0, "height": 0, "confidence": 0.95}]} ' 
                'where x,y,width,height are the bounding box coordinates ' 
                'and confidence is between 0 and 1.'
            )
            
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        for attempt in range(self.retry_config.max_retries):
            try:
                # Try to extract text
                ocr_dict = self._call_ollama_ocr(image_path, prompt, language)
                
                # Convert the dictionary to an OCRResult object
                ocr_result = OCRResult(
                    text=ocr_dict.get('text', ''),
                    language=language,
                    confidence=float(ocr_dict.get('confidence', 0.0)),
                    model=self.model,
                    metadata={
                        'model': self.model,
                        'image_path': str(image_path),
                        'attempt': attempt + 1,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )
                
                # Add text blocks if available
                if 'blocks' in ocr_dict and isinstance(ocr_dict['blocks'], list):
                    for block_data in ocr_dict['blocks']:
                        ocr_result.blocks.append(TextBlock(
                            text=block_data.get('text', ''),
                            x=float(block_data.get('x', 0)),
                            y=float(block_data.get('y', 0)),
                            width=float(block_data.get('width', 0)),
                            height=float(block_data.get('height', 0)),
                            confidence=float(block_data.get('confidence', 0.95)),
                            language=block_data.get('language', language),
                            metadata=block_data.get('metadata', {})
                        ))
                
                # If we get here, the operation was successful
                self.logger.info(
                    f"Successfully extracted text from {image_path}",
                    extra={'attempt': attempt + 1}
                )
                return ocr_result
                
            except (RuntimeError, ValueError, TimeoutError) as e:
                if attempt == self.retry_config.max_retries - 1:
                    # This was the last attempt, re-raise the exception
                    self.logger.error(
                        f"All {self.retry_config.max_retries} attempts failed for {image_path}",
                        extra={'attempt': attempt + 1, 'error': str(e)}
                    )
                    raise
                    
                # Log the error and wait before retrying
                wait_time = self.retry_config.calculate_delay(attempt + 1)
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {e}",
                    extra={'attempt': attempt + 1, 'error': str(e)}
                )
                time.sleep(wait_time)
    
    def _parse_ollama_output(
        self,
        output: str,
        language: str = "polish"
    ) -> OCRResult:
        """Parse the output from Ollama into an OCRResult.
        
        Args:
            output: Raw output from Ollama
            language: Language of the text
            
        Returns:
            Parsed OCRResult
            
        Raises:
            ValueError: If the output cannot be parsed
        """
        # Try to extract JSON from the output
        json_str = self._extract_json(output)
        
        if not json_str:
            # If no JSON found, treat the entire output as plain text
            return OCRResult(
                text=output.strip(),
                language=language,
                confidence=0.5  # Low confidence for unparsed output
            )
        
        try:
            # Parse the JSON
            data = json.loads(json_str)
            
            # Create the result
            result = OCRResult(
                text=data.get('text', ''),
                language=data.get('language', language),
                confidence=float(data.get('confidence', 0.0)),
                model=self.model
            )
            
            # Add text blocks if available
            if 'blocks' in data and isinstance(data['blocks'], list):
                for block_data in data['blocks']:
                    result.blocks.append(TextBlock(
                        text=block_data.get('text', ''),
                        x=float(block_data.get('x', 0)),
                        y=float(block_data.get('y', 0)),
                        width=float(block_data.get('width', 0)),
                        height=float(block_data.get('height', 0)),
                        confidence=float(block_data.get('confidence', 0.95)),
                        language=block_data.get('language', language),
                        metadata=block_data.get('metadata', {})
                    ))
            
            return result
            
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            self.logger.warning(
                f"Failed to parse Ollama output: {e}",
                extra={"output_sample": output[:200] + '...' if len(output) > 200 else output}
            )
            # Fall back to treating the output as plain text
            return OCRResult(
                text=output.strip(),
                language=language,
                confidence=0.3  # Very low confidence for failed parse
            )
    
    def _extract_json(self, text: str) -> str:
        """Extract a JSON object from a string."""
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # Try to find JSON array
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return ""
    
    def batch_process(
        self,
        image_paths: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
        save_intermediate: bool = True,
        **kwargs
    ) -> Dict[Path, OCRResult]:
        """Process multiple images in batch.
        
        Args:
            image_paths: List of paths to input images
            output_dir: Directory to save results (if save_intermediate is True)
            save_intermediate: Whether to save intermediate results
            **kwargs: Additional arguments to pass to extract_text()
            
        Returns:
            Dictionary mapping input paths to OCRResult objects
        """
        results = {}
        
        # Create output directory if needed
        if save_intermediate and output_dir is not None:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        for image_path in image_paths:
            try:
                image_path = Path(image_path)
                self.logger.info(f"Processing {image_path.name}")
                
                # Process the image
                result = self.extract_text(image_path, **kwargs)
                results[image_path] = result
                
                # Save the result if requested
                if save_intermediate and output_dir is not None:
                    output_path = output_dir / f"{image_path.stem}_result.json"
                    self._save_result(result, output_path)
                
            except Exception as e:
                self.logger.error(
                    f"Failed to process {image_path}: {e}",
                    exc_info=True
                )
                results[image_path] = OCRResult(
                    text="",
                    error=str(e),
                    metadata={
                        'success': False,
                        'error': str(e),
                        'image_path': str(image_path)
                    }
                )
        
        return results
    
    def _save_result(self, result: OCRResult, output_path: Path) -> None:
        """Save an OCR result to a file.
        
        Args:
            result: The OCR result to save
            output_path: Path where to save the result
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.debug(f"Saved result to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save result to {output_path}: {e}")
