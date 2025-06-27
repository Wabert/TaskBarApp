# pinned_windows.py (modified)
"""
Pinned windows section for SuiteView Taskbar
Manages the pinned window buttons in the taskbar
Modified to blend seamlessly with taskbar
"""

import tkinter as tk
from config import Colors, Fonts, Settings
from window_manager import ManagedWindow, WindowManager
from ui_components import ConfirmationDialog
import win32gui
import win32con

class PinnedWindowButton(tk.Frame):
    """Individual pinned window button with app-specific colors"""
    
    def __init__(self, parent, window: ManagedWindow, window_manager: WindowManager, 
                 on_unpin_callback):
        super().__init__(parent, bg=Colors.DARK_GREEN, bd=0, highlightthickness=0)
        self.window = window
        self.window_manager = window_manager
        self.on_unpin_callback = on_unpin_callback
        
        # Create button
        self.create_button()
        
        # Bind right-click for unpin
        self.button.bind("<Button-3>", self.show_unpin_menu)
    
    def create_button(self):
        """Create the toggle button with app-specific colors"""
        # Get app colors
        bg_color = self.window.colors['bg']
        fg_color = self.window.colors['fg']
        
        # Use shortened display name (without app prefix)
        display_text = self.window.display_name
        
        # Truncate if too long
        max_chars = 12
        if len(display_text) > max_chars:
            display_text = display_text[:max_chars-2] + ".."
        
        self.button = tk.Button(self, text=display_text,
                               bg=bg_color, fg=fg_color,
                               relief=tk.RAISED, bd=2,
                               width=6,  # Slightly wider for better text fit
                               font=('Arial', 8),
                               padx=0,
                               cursor='hand2',
                               wraplength=40,  # Allow text wrapping
                               activebackground=self._lighten_color(bg_color),
                               activeforeground=fg_color,
                               command=self.bring_window_to_front)
        self.button.pack(fill=tk.BOTH, expand=True)
        
        # Update visual state if window is hidden
        if self.window.is_hidden:
            self.button.configure(relief=tk.SUNKEN, bd=1)
    
    def _lighten_color(self, hex_color):
        """Lighten a hex color for hover effect"""
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten by 20%
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def bring_window_to_front(self):
        """Toggle window - hide if fully visible/on top, otherwise bring to front"""
        
        try:
            import win32gui
            
            if self.window.is_hidden:
                self.window_manager.toggle_window_visibility(self.window)

            self.window.bring_to_front()

                
                
                # Window is visible - check if it's the foreground window
                # current_foreground = win32gui.GetForegroundWindow()
                
                # # Check if window is minimized
                # if win32gui.IsIconic(self.window.hwnd):
                #     print(f"Window {self.window.display_name} is minimized - restoring")
                #     self.window.bring_to_front()
                # elif current_foreground == self.window.hwnd:
                #     # Window is the foreground window - hide it
                #     print(f"Window {self.window.display_name} is foreground - hiding")
                #     self.window_manager.toggle_window_visibility(self.window)
                # else:
                #     # Window is visible but not foreground - bring it to front
                #     print(f"Window {self.window.display_name} is not foreground - bringing to front")
                #     self.window.bring_to_front()
                
        except Exception as e:
            print(f"Error in bring_window_to_front: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to just bringing to front
            self.window.bring_to_front()
            
        # Don't update appearance - keep button color consistent
    
    def show_unpin_menu(self, event):
        """Show right-click menu for unpinning"""
        # Get taskbar position for proper dialog placement
        taskbar = self.winfo_toplevel()
        taskbar_x = taskbar.winfo_x()
        taskbar_y = taskbar.winfo_y()
        
        # Get button position relative to taskbar
        button_x = self.winfo_rootx()
        
        # Create custom confirmation dialog positioned above taskbar
        dialog = UnpinConfirmationDialog(
            taskbar,
            self.window.app_name,
            button_x,
            taskbar_y
        )
        
        # Wait for dialog result
        taskbar.wait_window(dialog)
        
        if dialog.result:
            self.window_manager.unpin_window(self.window)
            self.on_unpin_callback()
            
        # Prevent event from propagating to parent widgets (taskbar)
        return 'break'

class PinnedWindowsSection(tk.Frame):
    """Section in taskbar for pinned windows - now blends with taskbar"""
    
    def __init__(self, parent, window_manager: WindowManager, on_pin_changed_callback=None):
        # Use same background as taskbar, no border
        super().__init__(parent, bg=Colors.DARK_GREEN, relief=tk.FLAT, bd=0)
        self.window_manager = window_manager
        self.pinned_buttons = {}
        self.on_pin_changed_callback = on_pin_changed_callback
        
        # Debug output
        # print(f"\n=== CREATING PINNED WINDOWS SECTION ===")
        # print(f"Parent: {parent}")
        # print(f"Window manager: {window_manager}")

        # Don't set a fixed width - let it expand based on content
        self.configure(height=40)  # Match taskbar height
        
        # Remove any visible border
        self.configure(highlightbackground=Colors.DARK_GREEN, highlightthickness=0)
        
        # Create container for buttons with no padding
        self.button_container = tk.Frame(self, bg=Colors.DARK_GREEN)
        self.button_container.pack(fill=tk.BOTH, expand=True)  # No padding
        
        # No empty state label - just leave it blank
        
        # print(f"PinnedWindowsSection created successfully: {self}")
        # print(f"=== END CREATING PINNED WINDOWS SECTION ===\n")
    
    def refresh(self):
        """Refresh the pinned windows display"""
        # print(f"\n=== PINNED SECTION REFRESH ===")
        # print(f"Current button count: {len(self.pinned_buttons)}")
        
        # Clear existing buttons
        for hwnd in list(self.pinned_buttons.keys()):
            print(f"Destroying old button for hwnd: {hwnd}")
            self.pinned_buttons[hwnd].destroy()
            del self.pinned_buttons[hwnd]
        
        # Get pinned windows
        pinned_windows = self.window_manager.get_pinned_windows()
        print(f"Found {len(pinned_windows)} pinned windows")
        
        if pinned_windows:
            # Create buttons for pinned windows
            for i, window in enumerate(pinned_windows):
                print(f"{i}. Creating button for: {window.display_name} (hwnd: {window.hwnd})")
                if window.is_valid():
                    button = PinnedWindowButton(
                        self.button_container, 
                        window, 
                        self.window_manager,
                        self.on_pin_changed
                    )
                    button.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)  # No padding, fill height
                    self.pinned_buttons[window.hwnd] = button
                    print(f"   Button created and packed")
                    
                    # Force update to ensure visibility
                    button.update()
                    self.button_container.update()
                else:
                    print(f"   Window is not valid!")
        
        # Force the section to update
        self.update_idletasks()
        # print(f"Button container visible: {self.button_container.winfo_viewable()}")
        # print(f"Section geometry: {self.winfo_width()}x{self.winfo_height()}")
        # print("=== END REFRESH ===\n")
    
    def on_pin_changed(self):
        """Called when a window is pinned/unpinned from the button"""
        # Refresh the pinned section
        self.refresh()
        
        # Also call the taskbar callback if it exists
        if self.on_pin_changed_callback:
            self.on_pin_changed_callback()


class UnpinConfirmationDialog(tk.Toplevel):
    """Custom unpin confirmation dialog positioned above taskbar"""
    
    def __init__(self, parent, app_name, button_x, taskbar_y):
        super().__init__(parent)
        self.result = False
        
        # Window setup
        self.overrideredirect(True)
        self.configure(bg=Colors.DARK_GREEN)
        self.attributes('-topmost', True)
        
        # Create main frame with border
        main_frame = tk.Frame(self, bg=Colors.DARK_GREEN, relief=tk.RAISED, bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create header
        header = tk.Frame(main_frame, bg=Colors.DARK_GREEN, height=25)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title with icon
        title_label = tk.Label(header, text="📌 Unpin Window", 
                             bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                             font=Fonts.DIALOG_TITLE)
        title_label.pack(side=tk.LEFT, padx=10, pady=3)
        
        # Close button
        close_btn = tk.Label(header, text="×", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                           font=('Arial', 12, 'bold'), cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=5)
        close_btn.bind("<Button-1>", lambda e: self.cancel())
        
        # Content area
        content = tk.Frame(main_frame, bg=Colors.LIGHT_GREEN)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pin icon
        icon_label = tk.Label(content, text="📌", bg=Colors.LIGHT_GREEN,
                            font=('Arial', 24))
        icon_label.pack(pady=5)
        
        # Message
        msg = f"Unpin '{app_name}' from taskbar?"
        msg_label = tk.Label(content, text=msg, bg=Colors.LIGHT_GREEN,
                           fg=Colors.BLACK, font=Fonts.DIALOG_LABEL)
        msg_label.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(content, bg=Colors.LIGHT_GREEN)
        button_frame.pack(pady=10)
        
        yes_btn = tk.Button(button_frame, text="Yes", 
                          bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                          command=self.yes, width=8,
                          font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        yes_btn.pack(side=tk.LEFT, padx=5)
        
        no_btn = tk.Button(button_frame, text="No", 
                         bg=Colors.INACTIVE_GRAY, fg=Colors.WHITE,
                         command=self.cancel, width=8,
                         font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        no_btn.pack(side=tk.LEFT, padx=5)
        
        # Set dialog size
        dialog_width = 350
        dialog_height = 200
        
        # Position dialog above taskbar, centered on button
        x = button_x - dialog_width // 2
        y = taskbar_y - dialog_height - 5  # 5px gap above taskbar
        
        # Ensure dialog stays on screen
        screen_width = self.winfo_screenwidth()
        if x < 0:
            x = 0
        elif x + dialog_width > screen_width:
            x = screen_width - dialog_width
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Focus on No button (safer default)
        no_btn.focus_set()
        
        # Bind keys
        self.bind('<Return>', lambda e: self.yes())
        self.bind('<Escape>', lambda e: self.cancel())
        
        # Make modal
        self.grab_set()
    
    def yes(self):
        """Yes button clicked"""
        self.result = True
        self.destroy()
    
    def cancel(self):
        """No button clicked or dialog cancelled"""
        self.result = False
        self.destroy()