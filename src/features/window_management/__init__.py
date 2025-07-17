"""
Window management features
"""
from .window_manager import WindowManager, ManagedWindow
from .windows_menu import WindowsMenu
from .pinned_windows import PinnedWindowsSection

__all__ = ['WindowManager', 'ManagedWindow', 'WindowsMenu', 'PinnedWindowsSection']