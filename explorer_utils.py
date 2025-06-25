# explorer_utils.py
"""
Utility functions for detecting and interacting with File Explorer windows
"""

import win32gui
import win32process
import psutil
from pathlib import Path
import os

class ExplorerDetector:
    """Utility class for detecting open File Explorer windows"""
    
    @staticmethod
    def get_open_explorer_folders():
        """
        Get a list of currently open File Explorer folder paths
        Returns list of folder paths, ordered by most recently active
        """
        explorer_folders = []
        
        def enum_window_callback(hwnd, folders_list):
            """Callback function for window enumeration"""
            try:
                # Check if window is visible
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                
                # Get window class name
                class_name = win32gui.GetClassName(hwnd)
                
                # Check if it's a File Explorer window
                if class_name in ['CabinetWClass', 'ExploreWClass']:
                    # Get process information
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    
                    try:
                        process = psutil.Process(pid)
                        if process.name().lower() == 'explorer.exe':
                            # Try to get the folder path from the window
                            folder_path = ExplorerDetector._get_explorer_path(hwnd)
                            if folder_path and os.path.exists(folder_path):
                                folders_list.append({
                                    'path': folder_path,
                                    'hwnd': hwnd,
                                    'title': win32gui.GetWindowText(hwnd)
                                })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
            except Exception as e:
                print(f"Error processing window {hwnd}: {e}")
                
            return True
        
        # Enumerate all top-level windows
        win32gui.EnumWindows(enum_window_callback, explorer_folders)
        
        # Sort by Z-order (topmost first) - approximate by hwnd order
        # The most recently active windows typically have higher hwnd values
        explorer_folders.sort(key=lambda x: x['hwnd'], reverse=True)
        
        return [folder['path'] for folder in explorer_folders]
    
    @staticmethod
    def _get_explorer_path(hwnd):
        """
        Extract the current folder path from a File Explorer window
        This uses the window title to determine the path
        """
        try:
            window_title = win32gui.GetWindowText(hwnd)
            
            # File Explorer titles usually contain the folder name
            # Try different approaches to extract the path
            
            # Method 1: Direct path in title (Windows 11 style)
            normalized_title = os.path.normpath(window_title)
            if os.path.exists(normalized_title):
                return normalized_title
            
            # Method 2: Parse common File Explorer title formats
            # Remove common prefixes/suffixes
            title_cleaned = window_title
            
            # Remove " - File Explorer" suffix if present
            if title_cleaned.endswith(' - File Explorer'):
                title_cleaned = title_cleaned[:-15]
            
            # Remove " - Windows Explorer" suffix if present  
            if title_cleaned.endswith(' - Windows Explorer'):
                title_cleaned = title_cleaned[:-18]
            
            # Normalize and check if cleaned title is a valid path
            title_cleaned = os.path.normpath(title_cleaned)
            if os.path.exists(title_cleaned):
                return title_cleaned
            
            # Method 3: Try to construct common paths
            common_paths = [
                os.path.expanduser('~'),  # User home
                os.path.expanduser('~/Desktop'),
                os.path.expanduser('~/Documents'),
                os.path.expanduser('~/Downloads'),
                'C:\\',
                'D:\\',
            ]
            
            for base_path in common_paths:
                potential_path = os.path.normpath(os.path.join(base_path, title_cleaned))
                if os.path.exists(potential_path):
                    return potential_path
            
            # Method 4: Check if it's a special folder name
            special_folders = {
                'Desktop': os.path.expanduser('~/Desktop'),
                'Documents': os.path.expanduser('~/Documents'),
                'Downloads': os.path.expanduser('~/Downloads'),
                'Pictures': os.path.expanduser('~/Pictures'),
                'Videos': os.path.expanduser('~/Videos'),
                'Music': os.path.expanduser('~/Music'),
                'This PC': os.path.expanduser('~'),
                'Computer': os.path.expanduser('~'),
            }
            
            if title_cleaned in special_folders:
                return os.path.normpath(special_folders[title_cleaned])
            
            # Method 5: Advanced COM-based approach (fallback)
            try:
                return ExplorerDetector._get_explorer_path_com(hwnd)
            except:
                pass
            
            return None
            
        except Exception as e:
            print(f"Error getting explorer path for window {hwnd}: {e}")
            return None
    
    @staticmethod
    def _get_explorer_path_com(hwnd):
        """
        Use COM interface to get the actual path from File Explorer
        This is more reliable but also more complex
        """
        try:
            import win32com.client
            
            # Get Shell Windows collection
            shell_windows = win32com.client.Dispatch("Shell.Application").Windows()
            
            for window in shell_windows:
                try:
                    # Check if this window matches our hwnd
                    if hasattr(window, 'HWND') and window.HWND == hwnd:
                        # Get the location URL and convert to path
                        location = window.LocationURL
                        if location.startswith('file:///'):
                            # Convert file URL to local path
                            import urllib.parse
                            path = urllib.parse.unquote(location[8:])  # Remove 'file:///'
                            path = path.replace('/', '\\')  # Convert to Windows path
                            # Normalize the path to fix any mixed slash issues
                            path = os.path.normpath(path)
                            if os.path.exists(path):
                                return path
                except:
                    continue
                    
        except Exception as e:
            print(f"COM approach failed: {e}")
            
        return None
    
    @staticmethod
    def get_topmost_explorer_folder():
        """
        Get the path of the topmost (most recently active) File Explorer folder
        Returns None if no File Explorer windows are open
        """
        folders = ExplorerDetector.get_open_explorer_folders()
        return folders[0] if folders else None
    
    @staticmethod
    def get_best_default_folder():
        """
        Get the best folder to use as default for scanning
        Priority: 1) Topmost Explorer folder, 2) User Documents, 3) User Home
        All paths are normalized to use consistent backslashes
        """
        # Try to get topmost explorer folder first
        explorer_folder = ExplorerDetector.get_topmost_explorer_folder()
        if explorer_folder:
            return os.path.normpath(explorer_folder)
        
        # Fallback to Documents folder
        documents_folder = os.path.expanduser('~/Documents')
        if os.path.exists(documents_folder):
            return os.path.normpath(documents_folder)
        
        # Final fallback to user home
        return os.path.normpath(os.path.expanduser('~'))


# Test function for debugging
def test_explorer_detection():
    """Test function to see what Explorer windows are detected"""
    print("Testing Explorer Detection...")
    
    folders = ExplorerDetector.get_open_explorer_folders()
    print(f"Found {len(folders)} open File Explorer folders:")
    
    for i, folder in enumerate(folders, 1):
        print(f"  {i}. {folder}")
    
    topmost = ExplorerDetector.get_topmost_explorer_folder()
    print(f"\nTopmost folder: {topmost}")
    
    best_default = ExplorerDetector.get_best_default_folder()
    print(f"Best default folder: {best_default}")


if __name__ == "__main__":
    test_explorer_detection()