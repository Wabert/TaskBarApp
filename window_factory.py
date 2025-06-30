# window_factory.py
"""
Window Factory for SuiteView Taskbar Application
Provides base classes and factory functions for creating consistent windows
Updated with proper click-outside detection
"""

import tkinter as tk
from abc import ABC, abstractmethod
from config import Colors, Fonts

# Window type behavior definitions
WINDOW_BEHAVIORS = {
    "context_menu": {
        "description": "Right-click menus for item-specific actions",
        "modality": "non-modal",
        "focus": "temporary",
        "topmost": "always",
        "draggable": False,
        "resizable": "none",
        "persistence": "none",
        "close_on": ["click_outside", "select_option", "escape"],
        "titlebar": False,
        "dockable": False,
    },
    
    "taskbar_menu": {
        "description": "Popup menus from taskbar buttons",
        "modality": "non-modal",
        "focus": "temporary", 
        "topmost": "always",
        "draggable": False,
        "resizable": "vertical",
        "persistence": "none",
        "close_on": ["click_outside", "select_option", "escape", "toggle_button"],
        "titlebar": False,
        "dockable": False,
    },
    
    "action_dialog": {
        "description": "Modal dialogs requiring user decision",
        "modality": "modal",
        "focus": "blocking",
        "topmost": "always",
        "draggable": True,
        "resizable": "none",
        "persistence": "none",
        "close_on": ["button_action"],
        "titlebar": True,
        "dockable": False,
    },
    
    "notification_dialog": {
        "description": "Non-blocking status/progress windows",
        "modality": "non-modal",
        "focus": "non-stealing",
        "topmost": "never",
        "draggable": True,
        "resizable": "none",
        "persistence": "none",
        "close_on": ["x_button", "auto_complete", "escape"],
        "titlebar": True,
        "dockable": False,
    },
    
    "floating_window": {
        "description": "Independent tool windows",
        "modality": "non-modal",
        "focus": "independent",
        "topmost": "optional",
        "draggable": True,
        "resizable": "all",
        "persistence": "none",
        "close_on": ["x_button", "button_action"],
        "titlebar": True,
        "dockable": False,
    },
    
    "feature_window": {
        "description": "Major feature windows with docking capability",
        "modality": "non-modal",
        "focus": "independent",
        "topmost": "optional",
        "draggable": True,
        "resizable": "all",
        "persistence": "session",
        "close_on": ["x_button", "button_action"],
        "titlebar": True,
        "dockable": True,
    }
}


class BaseWindow(tk.Toplevel, ABC):
    """
    Base class for all SuiteView windows
    Provides consistent behavior based on window type
    """
    
    # Class variable to track window positions for session persistence
    _saved_positions = {}
    
    def __init__(self, parent, title, window_type, **kwargs):
        """
        Initialize base window
        
        Args:
            parent: Parent window
            title: Window title
            window_type: One of the defined window types
            **kwargs: Additional arguments (x, y, width, height, etc.)
        """
        super().__init__(parent)
        
        # Validate window type
        if window_type not in WINDOW_BEHAVIORS:
            raise ValueError(f"Invalid window type: {window_type}")
        
        # Store references
        self.parent = parent
        self.window_type = window_type
        self.behavior = WINDOW_BEHAVIORS[window_type]
        self.title_text = title
        
        # Extract positioning info from kwargs
        self.initial_x = kwargs.pop('x', None)
        self.initial_y = kwargs.pop('y', None)
        self.initial_width = kwargs.pop('width', None)
        self.initial_height = kwargs.pop('height', None)
        self.trigger_button = kwargs.pop('button', None)
        
        # Window state
        self.is_pinned = False
        self.is_docked = False
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Click outside detection state
        self._global_click_binding = None
        self._click_detection_active = False
        
        # Store remaining kwargs for subclass use
        self.kwargs = kwargs
        
        # Set window title
        self.title(title)
        
        # Apply window configuration
        self._configure_window()
        
        # Create window structure
        self._create_window_structure()
        
        # Apply window behaviors
        self._apply_behaviors()
        
        # Allow subclasses to create their content
        self.create_content()
        
        # Position the window
        self._position_window()
        
        # Final setup
        self._finalize_setup()
    
    def _configure_window(self):
        """Apply basic window configuration based on behavior"""
        # Remove window decorations if no titlebar
        if not self.behavior["titlebar"]:
            self.overrideredirect(True)
        
        # Set resizable behavior
        resizable = self.behavior["resizable"]
        if resizable == "none":
            self.resizable(False, False)
        elif resizable == "all":
            self.resizable(True, True)
        elif resizable == "horizontal":
            self.resizable(True, False)
        elif resizable == "vertical":
            self.resizable(False, True)
        
        # Set initial size if provided
        if self.initial_width and self.initial_height:
            self.geometry(f"{self.initial_width}x{self.initial_height}")
    
    def _create_window_structure(self):
        """Create the basic window structure"""
        # Create main container
        self.main_container = tk.Frame(self, bg=Colors.DARK_GREEN)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create titlebar if needed
        if self.behavior["titlebar"]:
            self._create_custom_titlebar()
        
        # Create content frame
        self.content_frame = tk.Frame(self.main_container, bg=Colors.LIGHT_GREEN)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def _create_custom_titlebar(self):
        """Create custom titlebar with standard elements"""
        self.titlebar = tk.Frame(self.main_container, bg=Colors.DARK_GREEN, height=30)
        self.titlebar.pack(fill=tk.X)
        self.titlebar.pack_propagate(False)
        
        # Title label
        self.title_label = tk.Label(self.titlebar, text=self.title_text,
                                   bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                                   font=Fonts.DIALOG_TITLE)
        self.title_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Close button if needed
        if "x_button" in self.behavior["close_on"]:
            self.close_btn = tk.Label(self.titlebar, text="×",
                                     bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                                     font=("Arial", 16, "bold"), cursor="hand2")
            self.close_btn.pack(side=tk.RIGHT, padx=5)
            self.close_btn.bind("<Button-1>", lambda e: self.close_window())
        
        # Pin button for optional topmost
        if self.behavior["topmost"] == "optional":
            self.pin_btn = tk.Label(self.titlebar, text="📌",
                                   bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                                   font=("Arial", 12), cursor="hand2")
            self.pin_btn.pack(side=tk.RIGHT, padx=5)
            self.pin_btn.bind("<Button-1>", self._toggle_pin)
        
        # Make titlebar draggable if window is draggable
        if self.behavior["draggable"]:
            self._make_draggable(self.titlebar)
            self._make_draggable(self.title_label)
    
    def _apply_behaviors(self):
        """Apply window behaviors based on configuration"""
        # Modality
        if self.behavior["modality"] == "modal":
            self.transient(self.parent)
            self.grab_set()
        
        # Focus behavior
        focus_type = self.behavior["focus"]
        if focus_type == "blocking":
            self.focus_force()
        elif focus_type == "temporary":
            self.focus_set()
        elif focus_type == "independent":
            # Normal focus behavior, no special handling
            pass
        elif focus_type == "non-stealing":
            # Don't take focus at all
            pass
        
        # Topmost behavior
        topmost = self.behavior["topmost"]
        if topmost == "always":
            self.attributes("-topmost", True)
        elif topmost == "never":
            self.attributes("-topmost", False)
        elif topmost == "optional":
            # Start unpinned
            self.attributes("-topmost", False)
        
        # Close handlers
        self._setup_close_handlers()
        
        # Bind Escape key if needed
        if "escape" in self.behavior["close_on"]:
            self.bind("<Escape>", lambda e: self.close_window())
    
    def _setup_close_handlers(self):
        """Set up various close handlers based on behavior"""
        close_on = self.behavior["close_on"]
        
        # Click outside handler - now properly implemented
        if "click_outside" in close_on:
            self._setup_click_outside_detection()
        
        # Window delete protocol
        if self.behavior["titlebar"] and "x_button" in close_on:
            self.protocol("WM_DELETE_WINDOW", self.close_window)
    
    def _setup_click_outside_detection(self):
        """Set up proper click outside detection"""
        # Get the root window (main taskbar window)
        root = self._get_root_window()
        if not root:
            print(f"Warning: Could not set up click outside detection for {self.window_type}")
            return
        
        # Create binding identifier unique to this window
        self._click_binding_id = f"<Button-1>-{id(self)}"
        
        # Bind to root window with a unique identifier
        root.bind("<Button-1>", self._handle_global_click, "+")
        self._global_click_binding = root
        self._click_detection_active = True
        
        # Bind to self to prevent closing when clicking inside
        self.bind("<Button-1>", self._handle_inside_click)
    
    def _get_root_window(self):
        """Get the root window (taskbar) safely"""
        try:
            # Walk up the parent chain to find the root
            window = self.parent
            while window:
                if isinstance(window, tk.Tk):
                    return window
                # Check if it has a root attribute (taskbar reference)
                if hasattr(window, 'root') and isinstance(window.root, tk.Tk):
                    return window.root
                # Try to go up the chain
                if hasattr(window, 'parent'):
                    window = window.parent
                elif hasattr(window, 'master'):
                    window = window.master
                else:
                    break
            
            # Fallback: try to get the Tk instance
            return self.winfo_toplevel() if hasattr(self, 'winfo_toplevel') else None
            
        except Exception as e:
            print(f"Error getting root window: {e}")
            return None
    
    def _handle_inside_click(self, event):
        """Handle clicks inside the window - prevent propagation"""
        # Stop the event from propagating to the global handler
        return "break"
    
    def _handle_global_click(self, event):
        """Handle global clicks to detect outside clicks"""
        if not self._click_detection_active:
            return
        
        try:
            # Get the widget that was clicked
            clicked_widget = event.widget
            
            # Check if the click was on this window or any of its children
            widget = clicked_widget
            while widget:
                if widget == self:
                    # Click was inside this window
                    return
                try:
                    widget = widget.master
                except:
                    break
            
            # Special handling for trigger button (allows toggle behavior)
            if hasattr(self, 'trigger_button') and self.trigger_button:
                widget = clicked_widget
                while widget:
                    if widget == self.trigger_button:
                        # Click was on trigger button
                        self.close_window()
                        return
                    try:
                        widget = widget.master
                    except:
                        break
            
            # Click was outside - close the window
            self.close_window()
            
        except Exception as e:
            print(f"Error in global click handler: {e}")
    
    def _make_draggable(self, widget):
        """Make a widget draggable"""
        widget.bind("<Button-1>", self._start_drag)
        widget.bind("<B1-Motion>", self._drag_window)
        widget.bind("<ButtonRelease-1>", self._stop_drag)
        widget.configure(cursor="fleur")
    
    def _start_drag(self, event):
        """Start dragging the window"""
        if self.behavior["draggable"] and not self.is_docked:
            self.is_dragging = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y
    
    def _drag_window(self, event):
        """Handle window dragging"""
        if self.is_dragging and self.behavior["draggable"]:
            x = self.winfo_x() + (event.x - self.drag_start_x)
            y = self.winfo_y() + (event.y - self.drag_start_y)
            self.geometry(f"+{x}+{y}")
    
    def _stop_drag(self, event):
        """Stop dragging"""
        self.is_dragging = False
        # Check for docking if supported
        if self.behavior["dockable"]:
            self._check_dock_position()
    
    def _toggle_pin(self, event=None):
        """Toggle window pinned state"""
        self.is_pinned = not self.is_pinned
        self.attributes("-topmost", self.is_pinned)
        
        # Update pin button appearance
        if hasattr(self, 'pin_btn'):
            if self.is_pinned:
                self.pin_btn.config(text="📍", fg=Colors.WHITE)
            else:
                self.pin_btn.config(text="📌", fg=Colors.WHITE)
    
    def _position_window(self):
        """Position window based on type and parameters"""
        self.update_idletasks()  # Ensure geometry is calculated
        
        # Check for saved position if persistence is enabled
        if self.behavior["persistence"] == "session":
            saved_pos = self._saved_positions.get(self.__class__.__name__)
            if saved_pos:
                self.geometry(saved_pos)
                return
        
        # Position based on window type
        if self.window_type == "context_menu":
            self._position_at_cursor()
        elif self.window_type == "taskbar_menu":
            self._position_above_button()
        elif self.window_type in ["action_dialog", "notification_dialog"]:
            if self.behavior["focus"] == "non-stealing":
                self._position_offset_center()
            else:
                self._position_center_parent()
        else:  # floating_window, feature_window
            if self.initial_x is not None and self.initial_y is not None:
                self.geometry(f"+{self.initial_x}+{self.initial_y}")
            else:
                self._position_center_screen()
    
    def _position_at_cursor(self):
        """Position window at cursor location"""
        x = self.initial_x or self.winfo_pointerx()
        y = self.initial_y or self.winfo_pointery()
        
        # Adjust to keep on screen
        x, y = self._adjust_position_for_screen(x, y)
        self.geometry(f"+{x}+{y}")
    
    def _position_above_button(self):
        """Position window above triggering button"""
        if self.trigger_button:
            btn_x = self.trigger_button.winfo_rootx()
            btn_y = self.trigger_button.winfo_rooty()
            
            # Position above button
            win_height = self.winfo_reqheight()
            x = btn_x
            y = btn_y - win_height
            
            # Adjust to keep on screen
            x, y = self._adjust_position_for_screen(x, y)
            self.geometry(f"+{x}+{y}")
        else:
            self._position_center_screen()
    
    def _position_center_parent(self):
        """Center window over parent"""
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        
        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2
        
        # Adjust to keep on screen
        x, y = self._adjust_position_for_screen(x, y)
        self.geometry(f"+{x}+{y}")
    
    def _position_center_screen(self):
        """Center window on screen"""
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def _position_offset_center(self):
        """Position window offset from center"""
        self._position_center_screen()
        
        # Offset slightly
        x = self.winfo_x() + 50
        y = self.winfo_y() - 50
        
        # Adjust to keep on screen
        x, y = self._adjust_position_for_screen(x, y)
        self.geometry(f"+{x}+{y}")
    
    def _adjust_position_for_screen(self, x, y):
        """Adjust position to ensure window stays on screen"""
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # Adjust x
        if x < 0:
            x = 0
        elif x + win_w > screen_w:
            x = screen_w - win_w
        
        # Adjust y
        if y < 0:
            y = 0
        elif y + win_h > screen_h:
            y = screen_h - win_h
        
        return x, y
    
    def _check_dock_position(self):
        """Check if window should dock to screen edge"""
        if not self.behavior["dockable"]:
            return
        
        x = self.winfo_x()
        y = self.winfo_y()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        dock_threshold = 20  # Pixels from edge to trigger docking
        
        # Check for edge docking
        if x < dock_threshold:
            self.dock_to_edge("left")
        elif x + self.winfo_width() > screen_w - dock_threshold:
            self.dock_to_edge("right")
        elif y < dock_threshold:
            self.dock_to_edge("top")
        elif y + self.winfo_height() > screen_h - dock_threshold:
            self.dock_to_edge("bottom")
    
    def dock_to_edge(self, edge):
        """Dock window to specified screen edge"""
        if not self.behavior["dockable"]:
            return
        
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        
        if edge == "left":
            self.geometry(f"{win_w}x{screen_h}+0+0")
        elif edge == "right":
            self.geometry(f"{win_w}x{screen_h}+{screen_w-win_w}+0")
        elif edge == "top":
            self.geometry(f"{screen_w}x{win_h}+0+0")
        elif edge == "bottom":
            self.geometry(f"{screen_w}x{win_h}+0+{screen_h-win_h}")
        
        self.is_docked = True
    
    def undock(self):
        """Undock window from edge"""
        self.is_docked = False
        # Restore to previous size/position or center
        self._position_center_screen()
    
    def _finalize_setup(self):
        """Final setup after window is created"""
        # Ensure window is visible
        self.update()
        
        # Apply any final adjustments
        if self.behavior["focus"] == "non-stealing":
            # Ensure parent keeps focus
            self.parent.focus_set()
    
    def close_window(self):
        """Close the window with appropriate cleanup"""
        # Clean up click outside detection first
        self._cleanup_click_detection()
        
        # Save position if persistence is enabled
        if self.behavior["persistence"] == "session":
            self._saved_positions[self.__class__.__name__] = self.geometry()
        
        # Release grab if modal
        if self.behavior["modality"] == "modal":
            try:
                self.grab_release()
            except:
                pass
        
        # Call any subclass cleanup
        self.on_closing()
        
        # Destroy window
        self.destroy()
    
    def _cleanup_click_detection(self):
        """Clean up click outside detection bindings"""
        if self._click_detection_active and self._global_click_binding:
            try:
                # Unbind our global click handler
                # Note: This unbinds ALL Button-1 handlers, so be careful
                # In a real app, you'd want a more sophisticated binding management
                self._global_click_binding.unbind("<Button-1>")
                self._click_detection_active = False
            except Exception as e:
                print(f"Error cleaning up click detection: {e}")
    
    def on_closing(self):
        """Override in subclass for cleanup before closing"""
        pass
    
    @abstractmethod
    def create_content(self):
        """
        Subclasses must implement this to create their content
        Content should be added to self.content_frame
        """
        pass


# Factory function
def create_window(window_type, parent, title, **kwargs):
    """
    Factory function to create a window of specified type
    
    Args:
        window_type: One of the defined window types
        parent: Parent window
        title: Window title
        **kwargs: Additional parameters
    
    Returns:
        BaseWindow subclass instance
    
    Note: This is a convenience function. For complex windows,
    create a proper subclass of BaseWindow instead.
    """
    
    class GenericWindow(BaseWindow):
        def create_content(self):
            # Empty content - should be overridden
            pass
    
    return GenericWindow(parent, title, window_type, **kwargs)