"""Configuration for retry behavior in the PDF OCR Processor."""

from dataclasses import dataclass, field
from typing import List, Type, Any, Optional, Callable


@dataclass
class RetryConfig:
    """Configuration for retry behavior.
    
    Attributes:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for exponential backoff
        retry_on: List of exception types to retry on
    """
    max_retries: int = 3
    initial_delay: float = 2.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    retry_on: List[Type[Exception]] = field(default_factory=lambda: [
        ConnectionError,
        TimeoutError,
        ValueError,
        RuntimeError,
        Exception
    ])
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate the delay for a retry attempt.
        
        Args:
            attempt: The current attempt number (1-based)
            
        Returns:
            The delay in seconds
        """
        delay = self.initial_delay * (self.backoff_factor ** (attempt - 1))
        return min(delay, self.max_delay)
    
    def should_retry(self, exception: Exception) -> bool:
        """Determine if an exception should trigger a retry.
        
        Args:
            exception: The exception that was raised
            
        Returns:
            bool: True if the operation should be retried
        """
        return any(isinstance(exception, exc_type) for exc_type in self.retry_on)
