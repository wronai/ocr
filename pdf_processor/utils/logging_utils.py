"""Logging utilities for the PDF OCR Processor."""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union
import json
from datetime import datetime

from ..config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add any extra attributes
        if hasattr(record, 'data') and isinstance(record.data, dict):
            log_data.update(record.data)
            
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(
    name: str = 'pdf_ocr_processor',
    log_level: Optional[Union[str, int]] = None,
    log_file: Optional[Union[str, Path]] = None,
    log_format: Optional[str] = None,
    json_format: bool = False
) -> logging.Logger:
    """Set up and configure a logger.
    
    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file (if None, logs to stderr)
        log_format: Log message format string
        json_format: Whether to use JSON format for logs
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't propagate to root logger
    logger.propagate = False
    
    # Set log level
    if log_level is None:
        log_level = LOG_LEVEL
    
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        if log_format is None:
            log_format = LOG_FORMAT
        formatter = logging.Formatter(log_format)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file is None and LOG_FILE:
        log_file = LOG_FILE
    
    if log_file:
        try:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to set up file logging to {log_file}: {e}")
    
    return logger


def log_execution_time(logger: logging.Logger):
    """Decorator to log the execution time of a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.debug(f"Starting {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.debug(
                    f"Completed {func.__name__} in {elapsed:.2f} seconds",
                    extra={'execution_time': elapsed, 'function': func.__name__}
                )
                return result
            except Exception as e:
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.error(
                    f"Error in {func.__name__} after {elapsed:.2f} seconds: {str(e)}",
                    extra={
                        'execution_time': elapsed,
                        'function': func.__name__,
                        'error': str(e),
                        'error_type': type(e).__name__
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_extra_data(logger: logging.Logger, level: int = logging.INFO, **kwargs):
    """Log additional data with a message.
    
    Args:
        logger: Logger instance to use
        level: Log level to use
        **kwargs: Data to include in the log
    """
    if not logger.isEnabledFor(level):
        return
    
    # Create a log record with the extra data
    record = logger.makeRecord(
        logger.name, level, "(extra_data)", 0, "", (), None, None
    )
    
    # Add the extra data to the record
    for key, value in kwargs.items():
        setattr(record, key, value)
    
    # Log the record
    logger.handle(record)
