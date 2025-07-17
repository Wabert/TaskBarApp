# utils.py
"""
Utility functions for SuiteView Taskbar Application
Contains Windows API calls, file operations, and common helper functions
"""

import ctypes
from ctypes import wintypes
import os
import webbrowser
from pathlib import Path
from ..core.config import WindowsAPI

class WindowsUtils:
    """Windows-specific utility functions"""
    
    @staticmethod
    def get_windows_taskbar_height():
        """Get the height of Windows taskbar"""
        try:
            work_area = wintypes.RECT()
            ctypes.windll.user32.SystemParametersInfoW(
                WindowsAPI.SPI_GETWORKAREA, 0, ctypes.byref(work_area), 0
            )
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
            taskbar_height = screen_height - work_area.bottom
            return taskbar_height if taskbar_height > 0 else 40
        except:
            return 40
    
    @staticmethod
    def get_screen_dimensions():
        """Get screen width and height"""
        try:
            width = ctypes.windll.user32.GetSystemMetrics(0)   # SM_CXSCREEN
            height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
            return width, height
        except:
            # Fallback values
            return 1920, 1080
    
    @staticmethod
    def set_window_topmost(window_id):
        """Force window to stay on top using Windows API"""
        try:
            hwnd = ctypes.windll.user32.GetParent(window_id)
            ctypes.windll.user32.SetWindowPos(
                hwnd, WindowsAPI.HWND_TOPMOST, 0, 0, 0, 0, 
                WindowsAPI.SWP_NOMOVE | WindowsAPI.SWP_NOSIZE
            )
        except:
            pass
    
    @staticmethod
    def get_work_area():
        """Get current desktop work area"""
        work_area = wintypes.RECT()
        try:
            ctypes.windll.user32.SystemParametersInfoW(
                WindowsAPI.SPI_GETWORKAREA, 0, ctypes.byref(work_area), 0
            )
            return work_area
        except:
            return None
    
    @staticmethod
    def set_work_area(rect):
        """Set desktop work area"""
        try:
            ctypes.windll.user32.SystemParametersInfoW(
                WindowsAPI.SPI_SETWORKAREA, 0, ctypes.byref(rect), 0
            )
            return True
        except:
            return False
    
    @staticmethod
    def restore_work_area(original_rect):
        """Restore original work area with proper flags"""
        try:
            ctypes.windll.user32.SystemParametersInfoW(
                WindowsAPI.SPI_SETWORKAREA, 0, ctypes.byref(original_rect), 
                WindowsAPI.SPIF_SENDCHANGE
            )
            return True
        except:
            return False

class FileUtils:
    """File and path utility functions"""
    
    @staticmethod
    def normalize_path(path):
        """
        Convert any path to Windows format with backslashes
        Handles forward slashes, mixed slashes, and Path objects
        """
        if not path:
            return ""
        
        # Convert Path object to string first
        if isinstance(path, Path):
            path = str(path)
        
        # Convert string paths
        path_str = str(path).strip()
        
        # Skip URLs
        if path_str.startswith(('http://', 'https://', 'www.')):
            return path_str
        
        # Convert forward slashes to backslashes and normalize
        normalized = os.path.normpath(path_str.replace('/', '\\'))
        
        return normalized
    
    @staticmethod
    def open_path(path, parent=None):
        """Open a file, folder, or URL"""
        try:
            # Normalize the path first
            normalized_path = FileUtils.normalize_path(path)
            
            if normalized_path.startswith(('http://', 'https://', 'www.')):
                webbrowser.open(normalized_path)
                return True
            elif os.path.exists(normalized_path):
                os.startfile(normalized_path)
                return True
            else:
                FileUtils._show_error(parent, "Error", f"Path not found: {normalized_path}")
                return False
        except Exception as e:
            FileUtils._show_error(parent, "Error", f"Could not open: {str(e)}")
            return False
    
    @staticmethod
    def _show_error(parent, title, message):
        """Show error dialog - uses custom dialog if parent provided, fallback to messagebox"""
        if parent:
            try:
                # Import here to avoid circular imports
                from ..ui.ui_components import ErrorDialog
                ErrorDialog.show(parent, title, message)
            except ImportError:
                # Fallback to standard messagebox if ui_components not available
                from tkinter import messagebox
                messagebox.showerror(title, message)
        else:
            # No parent provided, use console output
            print(f"{title}: {message}")
    
    @staticmethod
    def validate_path(path):
        """Validate if a path exists or is a valid URL"""
        if not path or not path.strip():
            return False
        
        path = path.strip()
        
        # Check if it's a URL
        if path.startswith(('http://', 'https://', 'www.')):
            return True
        
        # Check if file/folder exists
        return os.path.exists(path)

class UIUtils:
    """UI-related utility functions"""
    
    @staticmethod
    def center_window(window, width, height):
        """Center a window on screen"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def apply_hover_effect(widget, normal_bg, hover_bg, normal_fg='black', hover_fg='white'):
        """Apply hover effect to a widget"""
        def on_enter(e):
            widget.configure(bg=hover_bg, fg=hover_fg)
            # Apply to children if they exist
            for child in widget.winfo_children():
                try:
                    child.configure(bg=hover_bg, fg=hover_fg)
                except:
                    pass
        
        def on_leave(e):
            widget.configure(bg=normal_bg, fg=normal_fg)
            # Apply to children if they exist
            for child in widget.winfo_children():
                try:
                    child.configure(bg=normal_bg, fg=normal_fg)
                except:
                    pass
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
        return on_enter, on_leave
    
    @staticmethod
    def create_separator(parent, bg_color, width=2):
        """Create a vertical separator"""
        import tkinter as tk
        separator = tk.Frame(parent, bg=bg_color, width=width)
        return separator