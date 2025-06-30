"""
Logging configuration for the Soccer Intelligence System.
"""

import logging
import logging.handlers
import os
from typing import Optional
from datetime import datetime

from .config import Config


def setup_logger(name: str = 'soccer_intelligence', 
                config: Optional[Config] = None,
                log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        config: Configuration object
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    if config is None:
        config = Config()
    
    # Get logging configuration
    log_level = config.get('logging.level', 'INFO')
    log_format = config.get('logging.format', 
                           '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file is None:
        log_file = config.get('logging.file', 'logs/soccer_intelligence.log')
    
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")


def log_execution_time(func):
    """Decorator to log function execution time."""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {e}")
            raise
    
    return wrapper


def log_api_call(func):
    """Decorator to log API calls."""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # Log the API call
        logger.info(f"Making API call: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"API call successful: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"API call failed: {func.__name__} - {e}")
            raise
    
    return wrapper
