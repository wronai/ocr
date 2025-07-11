"""
Ollama API client for OCR processing.

This module provides a client for interacting with the Ollama API for OCR tasks.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..config.settings import DEFAULT_OCR_MODEL, DEFAULT_TIMEOUT
from ..models.retry_config import RetryConfig
from ..utils.logging_utils import log_execution_time, setup_logger
from ..utils.validation_utils import validate_image_file

class OllamaClient:
    """Client for interacting with the Ollama API for OCR tasks."""
    
    def __init__(
        self,
        model: str = DEFAULT_OCR_MODEL,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: Optional[RetryConfig] = None
    ) -> None:
        """Initialize the Ollama client.
        
        Args:
            model: Name of the Ollama model to use for OCR
            timeout: Timeout in seconds for API requests
            retry_config: Configuration for retrying failed requests
        """
        self.logger = setup_logger('ollama_client')
        self.model = model
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()
        self._check_ollama_available()
    
    def _check_ollama_available(self) -> None:
        """Check if Ollama is installed and the specified model is available."""
        try:
            # Check if ollama command is available
            subprocess.run(
                ["ollama", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            
            # Check if the model is available
            result = subprocess.run(
                ["ollama", "list"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            
            if self.model not in result.stdout:
                self.logger.warning(
                    f"Model '{self.model}' is not available locally. "
                    f"Available models: {result.stdout}"
                )
                
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            raise RuntimeError(
                "Ollama is not installed or not in PATH. "
                "Please install Ollama from https://ollama.ai/"
            ) from e
    
    @log_execution_time(setup_logger('ollama_client'))
    def extract_text(
        self,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
        language: str = "polish"
    ) -> Dict[str, Any]:
        """Extract text from an image using the Ollama API.
        
        Args:
            image_path: Path to the image file
            prompt: Custom prompt to use for the OCR model
            language: Language of the text in the image
            
        Returns:
            Dictionary containing the raw OCR results
            
        Raises:
            RuntimeError: If the Ollama command fails
            ValueError: If the output cannot be parsed
            TimeoutError: If the operation times out
        """
        image_path = Path(image_path)
        validate_image_file(image_path)
        
        # Prepare the prompt
        if prompt is None:
            prompt = (
                "Extract all text from this image in {language}. "
                "Return a JSON object with the following structure: "
                "{\"text\": \"full text\", \"blocks\": [{\"text\": \"...\", "
                "\"x\": 0.0, \"y\": 0.0, \"width\": 0.0, \"height\": 0.0, "
                "\"confidence\": 0.95}]}"
            )
        
        prompt = prompt.format(language=language)
        
        # Build the command
        cmd = [
            "ollama", "run",
            "--timeout", str(self.timeout),
            self.model,
            f"{prompt} <image>"
        ]
        
        try:
            # Run the command
            result = subprocess.run(
                cmd,
                input=image_path.read_bytes(),
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                raise RuntimeError(f"Ollama command failed: {error_msg}")
            
            # Parse the output
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                # Try to extract JSON from the output
                try:
                    # Look for JSON in the output
                    json_start = result.stdout.find('{')
                    json_end = result.stdout.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        output = json.loads(result.stdout[json_start:json_end])
                    else:
                        raise ValueError("No valid JSON found in the output") from e
                except (ValueError, json.JSONDecodeError) as e2:
                    raise ValueError(
                        f"Failed to parse Ollama output: {result.stdout}"
                    ) from e2
            
            return output
            
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(
                f"OCR processing timed out after {self.timeout} seconds"
            ) from e
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Ollama command failed with return code {e.returncode}: {e.stderr}"
            ) from e
