# window_manager.py (fixed)
"""
Windows detection and management functionality for SuiteView Taskbar
Handles window enumeration, filtering, hiding/showing, and pinning
Fixed to properly restore minimized windows
"""

import win32gui
import win32api
import win32con
import win32process
import psutil
from typing import List, Dict, Optional
import re

class ManagedWindow:
    """Represents a managed window with its state"""
    
    def __init__(self, hwnd: int, title: str, process_name: str):
        self.hwnd = hwnd
        self.title = title
        self.process_name = process_name
        self.app_name = self._extract_app_name()
        self.display_name = self._create_display_name()
        self.is_hidden = False
        self.is_pinned = False
        self.original_ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    
    def _extract_app_name(self) -> str:
        """Extract application name from process name"""
        # Remove .exe extension
        app = self.process_name.replace('.exe', '')
        
        # Capitalize common apps
        common_apps = {
            'chrome': 'Chrome',
            'firefox': 'Firefox',
            'winword': 'Word',
            'excel': 'Excel',
            'powerpnt': 'PowerPoint',
            'outlook': 'Outlook',
            'notepad': 'Notepad',
            'notepad++': 'Notepad++',
            'code': 'VS Code',
            'devenv': 'Visual Studio',
            'acrobat': 'Acrobat',
            'acrord32': 'Acrobat Reader',
            'explorer': 'File Explorer'
        }
        
        return common_apps.get(app.lower(), app.title())
    
    def _create_display_name(self) -> str:
        """Create display name in format 'AppName - WindowTitle'"""
        if self.title.startswith(self.app_name):
            # Avoid duplication if app name is already in title
            return self.title
        return f"{self.app_name} - {self.title}"
    
    def hide(self) -> bool:
        """Hide the window (remove from Alt+Tab and taskbar)"""
        try:
            # Get current extended style
            ex_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
            
            # Add WS_EX_TOOLWINDOW to hide from Alt+Tab and taskbar
            new_ex_style = ex_style | win32con.WS_EX_TOOLWINDOW
            
            # Remove WS_EX_APPWINDOW to ensure it's hidden from taskbar
            new_ex_style = new_ex_style & ~win32con.WS_EX_APPWINDOW
            
            # Apply new style
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, new_ex_style)
            
            # Hide the window
            win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)
            
            self.is_hidden = True
            return True
        except Exception as e:
            print(f"Error hiding window {self.display_name}: {e}")
            return False
    
    def show(self) -> bool:
        """Show the window (restore to Alt+Tab and taskbar)"""
        try:
            # Restore original extended style
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, self.original_ex_style)
            
            # Show the window
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
            
            self.is_hidden = False
            return True
        except Exception as e:
            print(f"Error showing window {self.display_name}: {e}")
            return False
    
    def bring_to_front(self) -> bool:
        """Bring window to front and give it focus, restoring from minimized if needed"""
        try:
            if self.is_hidden:
                self.show()
            
            # Check if window is minimized (iconic)
            if win32gui.IsIconic(self.hwnd):
                print(f"Window {self.display_name} is minimized, restoring...")
                # Restore the window from minimized state
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            elif not win32gui.IsWindowVisible(self.hwnd):
                # Window is hidden but not minimized
                win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
            
            # Bring window to foreground
            # Sometimes SetForegroundWindow fails, so we try a few methods
            try:
                win32gui.SetForegroundWindow(self.hwnd)
            except:
                # Alternative method: simulate alt key to allow focus change
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32gui.SetForegroundWindow(self.hwnd)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # Ensure window is active
            win32gui.SetActiveWindow(self.hwnd)
            
            return True
        except Exception as e:
            print(f"Error bringing window to front {self.display_name}: {e}")
            return False
    
    def is_valid(self) -> bool:
        """Check if window still exists"""
        return win32gui.IsWindow(self.hwnd)


class WindowManager:
    """Manages window detection, filtering, and state"""
    
    def __init__(self):
        self.managed_windows: Dict[int, ManagedWindow] = {}
        self.excluded_processes = {
            'searchui.exe', 'shellexperiencehost.exe',
            'applicationframehost.exe', 'systemsettings.exe', 'textinputhost.exe',
            'lockapp.exe', 'searchapp.exe', 'startmenuexperiencehost.exe',
            'runtimebroker.exe', 'svchost.exe', 'system', 'registry',
            'smss.exe', 'csrss.exe', 'wininit.exe', 'services.exe',
            'lsass.exe', 'winlogon.exe', 'dwm.exe', 'taskhostw.exe',
            'searchindexer.exe', 'backgroundtaskhost.exe'
        }
    
    def get_relevant_windows(self) -> List[ManagedWindow]:
        """Get all relevant open windows on current desktop"""
        windows = []
        
        def enum_callback(hwnd, _):
            if self._is_relevant_window(hwnd):
                try:
                    title = win32gui.GetWindowText(hwnd)
                    if title:  # Skip windows with no title
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        process_name = process.name()
                        
                        # Check if we already manage this window
                        if hwnd in self.managed_windows:
                            window = self.managed_windows[hwnd]
                            # Update title in case it changed
                            window.title = title
                            window.display_name = window._create_display_name()
                        else:
                            window = ManagedWindow(hwnd, title, process_name)
                            self.managed_windows[hwnd] = window
                        
                        windows.append(window)
                except Exception as e:
                    print(f"Error processing window {hwnd}: {e}")
            return True
        
        win32gui.EnumWindows(enum_callback, None)
        
        # Clean up managed windows that no longer exist
        self._cleanup_invalid_windows()
        
        return sorted(windows, key=lambda w: w.display_name.lower())
    
    def _is_relevant_window(self, hwnd: int) -> bool:
        """Check if window is relevant (user-facing, not system)"""
        try:
            # Window must be visible or minimized (but not completely hidden)
            if not win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd):
                return False
            
            # Get window info
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            process_name = process.name().lower()
            
            # Special handling for explorer.exe - we want File Explorer windows but not the desktop/taskbar
            if process_name == 'explorer.exe':
                # Get window class name to distinguish File Explorer from desktop/taskbar
                class_name = win32gui.GetClassName(hwnd)
                # File Explorer windows have these class names
                if class_name not in ['CabinetWClass', 'ExploreWClass']:
                    return False
            elif process_name in self.excluded_processes:
                # Exclude other system processes
                return False
            
            # Get window style
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            
            # Must be a normal window (not a tool window, unless we made it one)
            if hwnd not in self.managed_windows:
                if ex_style & win32con.WS_EX_TOOLWINDOW:
                    return False
            
            # Should have a title bar or be a notable window
            if not (style & win32con.WS_CAPTION):
                # Some apps like Chrome have windows without WS_CAPTION
                # Check if it's a main window by other criteria
                if not (ex_style & win32con.WS_EX_APPWINDOW):
                    return False
            
            # Check if it's a main window (not a dialog or popup)
            owner = win32gui.GetWindow(hwnd, win32con.GW_OWNER)
            if owner:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _cleanup_invalid_windows(self):
        """Remove windows that no longer exist from managed windows"""
        invalid_hwnds = []
        for hwnd, window in self.managed_windows.items():
            if not window.is_valid():
                invalid_hwnds.append(hwnd)
        
        for hwnd in invalid_hwnds:
            del self.managed_windows[hwnd]
    
    def toggle_window_visibility(self, window: ManagedWindow) -> bool:
        """Toggle window visibility"""
        if window.is_hidden:
            return window.show()
        else:
            return window.hide()
    
    def pin_window(self, window: ManagedWindow):
        """Mark window as pinned"""
        window.is_pinned = True
    
    def unpin_window(self, window: ManagedWindow):
        """Unpin window and ensure it's visible"""
        window.is_pinned = False
        if window.is_hidden:
            window.show()
    
    def unhide_all_windows(self):
        """Unhide all hidden windows (for app cleanup)"""
        for window in self.managed_windows.values():
            if window.is_hidden:
                window.show()
    
    def get_pinned_windows(self) -> List[ManagedWindow]:
        """Get all currently pinned windows"""
        return [w for w in self.managed_windows.values() if w.is_pinned]
    
    # Close a managed window and remove it from the managed_windows dictionary
    def close_managed_window(self, window: ManagedWindow):
        """Close the window"""
        del self.managed_windows[window.hwnd] 
        win32gui.PostMessage(window.hwnd, win32con.WM_CLOSE, 0, 0)
        # win32gui.CloseWindow(window.hwnd)