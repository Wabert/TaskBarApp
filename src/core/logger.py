"""
Logging configuration for SuiteView Taskbar Application
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class TaskbarLogger:
    """Centralized logging configuration for the application"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskbarLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Set up the logger with file and console handlers"""
        # Create logger
        self._logger = logging.getLogger('TaskbarApp')
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers = []  # Clear any existing handlers
        
        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # File handler - detailed logging
        log_file = log_dir / f'taskbar_{datetime.now().strftime("%Y-%m-%d")}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)
        
        # Console handler - important messages only
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)
        
        # Log startup
        self._logger.info("TaskbarApp logging initialized")
        self._logger.debug(f"Log file: {log_file}")
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance
        
        Args:
            name: Optional module name for the logger
            
        Returns:
            Logger instance
        """
        if name:
            return logging.getLogger(f'TaskbarApp.{name}')
        return self._logger
    
    def set_console_level(self, level: str):
        """Change console logging level
        
        Args:
            level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        level_obj = getattr(logging, level.upper(), logging.INFO)
        for handler in self._logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(level_obj)
                self._logger.info(f"Console logging level set to {level}")
    
    def set_file_level(self, level: str):
        """Change file logging level
        
        Args:
            level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        level_obj = getattr(logging, level.upper(), logging.DEBUG)
        for handler in self._logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(level_obj)
                self._logger.info(f"File logging level set to {level}")
    
    def add_context(self, **kwargs):
        """Add context to all log messages
        
        Args:
            **kwargs: Context key-value pairs
        """
        adapter = logging.LoggerAdapter(self._logger, kwargs)
        return adapter


# Convenience function to get logger
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance
    
    Args:
        name: Optional module name for the logger
        
    Returns:
        Logger instance
    """
    return TaskbarLogger().get_logger(name)


# Convenience function to setup logging (call once at startup)
def setup_logging():
    """Initialize the logging system"""
    TaskbarLogger()


# Convenience decorators for logging function calls
def log_function_call(func):
    """Decorator to log function entry and exit"""
    logger = get_logger(func.__module__)
    
    def wrapper(*args, **kwargs):
        logger.debug(f"Entering {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__}")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise
    
    return wrapper


def log_errors(func):
    """Decorator to log exceptions"""
    logger = get_logger(func.__module__)
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise
    
    return wrapper


# Example usage in other modules:
# from .logger import get_logger
# logger = get_logger(__name__)
# logger.info("This is an info message")
# logger.debug("This is a debug message")
# logger.warning("This is a warning")
# logger.error("This is an error")