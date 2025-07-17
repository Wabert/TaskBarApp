"""
Core modules for TaskbarApp
"""
from .taskbar import SuiteViewTaskbar
from .config import *
from .logger import setup_logging, get_logger

__all__ = ['SuiteViewTaskbar', 'setup_logging', 'get_logger']