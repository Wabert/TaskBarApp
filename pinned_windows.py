# pinned_windows.py
"""
Pinned windows section for SuiteView Taskbar
Manages the pinned window buttons in the taskbar
"""

import tkinter as tk
from config import Colors, Fonts, Settings
from window_manager import ManagedWindow, WindowManager
from ui_components import ConfirmationDialog

class PinnedWindowButton(tk.Frame):
    """Individual pinned window button"""
    
    def __init__(self, parent, window: ManagedWindow, window_manager: WindowManager, 
                 on_unpin_callback):
        super().__init__(parent, bg=Colors.DARK_GREEN)
        self.window = window
        self.window_manager = window_manager
        self.on_unpin_callback = on_unpin_callback
        
        # Create button
        self.create_button()
        
        # Bind right-click for unpin
        self.button.bind("<Button-3>", self.show_unpin_menu)
    
    def create_button(self):
        """Create the toggle button"""
        print(f"\n=== CREATING PINNED BUTTON ===")
        print(f"Window: {self.window.display_name}")
        print(f"Parent: {self.master}")
        
        # Determine colors based on visibility
        bg_color = Colors.WINDOW_VISIBLE if not self.window.is_hidden else Colors.WINDOW_HIDDEN
        fg_color = Colors.BLACK if not self.window.is_hidden else Colors.WHITE
        
        # Use app name with word wrapping instead of truncating
        display_text = self.window.app_name
        
        # Create smaller font for button text
        button_font = (Fonts.TASKBAR_BUTTON[0], Fonts.TASKBAR_BUTTON[1] - 2)
        
        self.button = tk.Button(self, text=display_text,
                               bg=bg_color, fg=fg_color,
                               relief=tk.RAISED, bd=2,
                               font=button_font,
                               width=6, height=2,  # More square: 6 chars wide, 2 lines high
                               cursor='hand2',
                               activebackground=Colors.HOVER_GREEN,
                               command=self.toggle_window,
                               wraplength=45,  # Enable word wrapping at ~45 pixels
                               justify=tk.CENTER)  # Center the wrapped text
        self.button.pack(padx=2, pady=2)
        
        # Force visibility
        self.button.update()
        
        print(f"Button created: {self.button}")
        print(f"Button visible: {self.button.winfo_viewable()}")
        print(f"Button geometry: {self.button.winfo_geometry()}")
        print(f"=== END CREATING PINNED BUTTON ===\n")
    
    def toggle_window(self):
        """Toggle window visibility"""
        # if self.window.is_hidden:
        #     self.window.bring_to_front()
        # else:
        #     self.window_manager.toggle_window_visibility(self.window)
        
        self.window.bring_to_front()
        self.update_appearance()
    
    def update_appearance(self):
        """Update button appearance based on window state"""
        bg_color = Colors.WINDOW_VISIBLE if not self.window.is_hidden else Colors.WINDOW_HIDDEN
        fg_color = Colors.BLACK if not self.window.is_hidden else Colors.WHITE
        self.button.configure(bg=bg_color, fg=fg_color)
    
    def show_unpin_menu(self, event):
        """Show right-click menu for unpinning"""
        result = ConfirmationDialog.ask(
            self.winfo_toplevel(),
            "Unpin Window",
            f"Unpin '{self.window.app_name}' from taskbar?",
            icon="📌"
        )
        
        if result:
            self.window_manager.unpin_window(self.window)
            self.on_unpin_callback()
            
        # Prevent event from propagating to parent widgets (taskbar)
        return 'break'

class PinnedWindowsSection(tk.Frame):
    """Section in taskbar for pinned windows"""
    
    def __init__(self, parent, window_manager: WindowManager, on_pin_changed_callback=None):
        super().__init__(parent, bg=Colors.PINNED_SECTION_BG, 
                        relief=tk.SUNKEN, bd=2)
        self.window_manager = window_manager
        self.pinned_buttons = {}
        self.on_pin_changed_callback = on_pin_changed_callback
        
        # Debug output
        print(f"\n=== CREATING PINNED WINDOWS SECTION ===")
        print(f"Parent: {parent}")
        print(f"Window manager: {window_manager}")

        # Set minimum and fixed size
        self.configure(width=Settings.PINNED_SECTION_WIDTH, height=35)
        self.pack_propagate(False)  # Maintain fixed size
        
        # Add a visible border to debug
        self.configure(highlightbackground=Colors.MEDIUM_GREEN, highlightthickness=1)
        
        # Create container for buttons with padding
        self.button_container = tk.Frame(self, bg=Colors.PINNED_SECTION_BG)
        self.button_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Create label for empty state
        self.empty_label = tk.Label(self.button_container, text="[Pinned Windows]", 
                                   bg=Colors.PINNED_SECTION_BG,
                                   fg=Colors.LIGHT_GREEN,
                                   font=(Fonts.TASKBAR_BUTTON[0], 
                                        Fonts.TASKBAR_BUTTON[1] - 2, 'italic'))
        
        # Start with empty state
        self.show_empty_state()

        print(f"PinnedWindowsSection created successfully: {self}")
        print(f"=== END CREATING PINNED WINDOWS SECTION ===\n")
    
    def refresh(self):
        """Refresh the pinned windows display"""
        print(f"\n=== PINNED SECTION REFRESH ===")
        print(f"Current button count: {len(self.pinned_buttons)}")
        
        # Clear existing buttons
        for hwnd in list(self.pinned_buttons.keys()):
            print(f"Destroying old button for hwnd: {hwnd}")
            self.pinned_buttons[hwnd].destroy()
            del self.pinned_buttons[hwnd]
        
        # Get pinned windows
        pinned_windows = self.window_manager.get_pinned_windows()
        print(f"Found {len(pinned_windows)} pinned windows")
        
        if not pinned_windows:
            print("No pinned windows - showing empty state")
            self.show_empty_state()
        else:
            print("Has pinned windows - hiding empty state")
            self.hide_empty_state()
            
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
                    button.pack(side=tk.LEFT, padx=2)
                    self.pinned_buttons[window.hwnd] = button
                    print(f"   Button created and packed")
                    
                    # Force update to ensure visibility
                    button.update()
                    self.button_container.update()
                else:
                    print(f"   Window is not valid!")
        
        # Force the section to update
        self.update_idletasks()
        print(f"Button container visible: {self.button_container.winfo_viewable()}")
        print(f"Section geometry: {self.winfo_width()}x{self.winfo_height()}")
        print("=== END REFRESH ===\n")
    
    def show_empty_state(self):
        """Show empty state label"""
        self.empty_label.pack(expand=True)
        
    def hide_empty_state(self):
        """Hide empty state label"""
        self.empty_label.pack_forget()
    
    def update_window_states(self):
        """Update appearance of all pinned window buttons"""
        for button in self.pinned_buttons.values():
            button.update_appearance()
    
    def on_pin_changed(self):
        """Called when a window is pinned/unpinned from the button"""
        # Refresh the pinned section
        self.refresh()
        
        # Also call the taskbar callback if it exists
        if self.on_pin_changed_callback:
            self.on_pin_changed_callback()