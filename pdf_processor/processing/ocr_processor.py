"""OCR processing using Ollama models."""

import json
import re
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union, Type
import tempfile
import shutil
import os

from PIL import Image
import numpy as np

from ..models.ocr_result import OCRResult, TextBlock
from ..models.retry_config import RetryConfig
from ..utils.validation_utils import validate_image_file, validate_positive_number
from ..utils.logging_utils import setup_logger, log_execution_time
from ..config.settings import (
    DEFAULT_OCR_MODEL,
    DEFAULT_TIMEOUT,
    OCR_CONFIDENCE_THRESHOLD
)


class OCRProcessor:
    """Handles OCR processing using Ollama models."""
    
    def __init__(
        self,
        model: str = DEFAULT_OCR_MODEL,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: Optional[RetryConfig] = None
    ):
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
        
        # Prepare the command
        cmd = [
            'ollama',
            'run',
            self.model,
            prompt
        ]
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if value is not None:
                cmd.extend([f"--{key}", str(value)])
        
        # Read the image data
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        if not image_data:
            raise ValueError(f"Empty image file: {image_path}")
        
        # Try multiple times if needed
        last_error = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Run the OCR command
                result = subprocess.run(
                    cmd,
                    input=image_data,
                    capture_output=True,
                    timeout=self.timeout
                )
                
                # Check for errors
                if result.returncode != 0:
                    error_msg = result.stderr.decode('utf-8', errors='replace')
                    raise RuntimeError(
                        f"Ollama error (code {result.returncode}): {error_msg}"
                    )
                
                # Parse the output
                output = result.stdout.decode('utf-8', errors='replace').strip()
                if not output:
                    raise ValueError("Empty response from Ollama")
                
                # Parse the OCR result
                ocr_result = self._parse_ollama_output(output, language)
                
                # Add metadata
                ocr_result.metadata.update({
                    'model': self.model,
                    'image_path': str(image_path),
                    'attempt': attempt + 1,
                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                })
                
                return ocr_result
                
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {e}",
                    extra={'attempt': attempt + 1, 'error': str(e)}
                )
                
                if attempt < self.retry_config.max_retries:
                    # Wait before retrying
                    delay = self.retry_config.calculate_delay(attempt + 1)
                    time.sleep(delay)
                else:
                    break
        
        # If we get here, all attempts failed
        raise RuntimeError(
            f"Failed to extract text after {self.retry_config.max_retries + 1} attempts. "
            f"Last error: {last_error}"
        )
    
    def _get_default_prompt(self, language: str = "polish") -> str:
        """Get the default prompt for OCR."""
        return (
            f"Extract all text from this image in {language} with high accuracy. "
            "Return a JSON object with the following structure: "
            "{\"text\": \"full text\", \"blocks\": [{\"text\": \"text\", "
            "\"x\": 0, \"y\": 0, \"width\": 0, \"height\": 0, "
            "\"confidence\": 0.95}]} "
            "where x,y,width,height are the bounding box coordinates and confidence is between 0 and 1."
        )
    
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
        """Save an OCR result to a file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.debug(f"Saved result to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save result to {output_path}: {e}")
