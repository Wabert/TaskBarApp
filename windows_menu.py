# windows_menu.py (modified)
"""
Windows menu UI for SuiteView Taskbar
Shows list of open windows with hide/pin functionality
Now excludes pinned windows from the list
"""

import tkinter as tk
from config import Colors, Fonts, Dimensions
from window_manager import WindowManager, ManagedWindow
from utils import WindowsUtils
from typing import Callable, Optional

class WindowsMenu(tk.Toplevel):
    """Windows management menu"""
    
    def __init__(self, taskbar, window_manager: WindowManager, on_pin_callback: Callable, 
                 stored_geometry: Optional[str] = None):
        super().__init__(taskbar.root)
        self.parent = taskbar


        self.window_manager = window_manager
        self.on_pin_callback = on_pin_callback
        self.stored_geometry = stored_geometry
                
        # Window setup
        self.title("")  # No title for custom window
        self.configure(bg=Colors.DARK_GREEN)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.98)
        
        # Important: Make window resizable
        self.resizable(True, True)
        
        # Remove default window decorations for custom look
        self.overrideredirect(True)
        
        # Track window items for updates
        self.window_items = {}
        
        # Resize variables
        self.is_resizing = False
        self.resize_edge = None
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.original_geometry = None
        
        # Main container with visible border
        self.main_frame = tk.Frame(self, bg=Colors.DARK_GREEN, relief=tk.RAISED, bd=3)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.create_header()
        
        # Create scrollable content area
        self.create_content_area()
        
        # Create resize handles
        self.create_resize_handles()
        
        # Populate with windows
        self.refresh_window_list()
        
        # Apply stored geometry or default size and position
        if stored_geometry:
            self.geometry(stored_geometry)
        else:
            # Set default size and position
            default_width = 600  # Slightly narrower
            
            # Calculate height based on number of windows with smaller item height
            window_count = len([w for w in self.window_manager.get_relevant_windows() if not w.is_pinned])
            base_height = 80   # Minimum height for header and padding
            item_height = 32   # Smaller height per window item
            max_height = 700   # Increased max height to show more items
            default_height = min(base_height + (window_count * item_height), max_height)

            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight() 

            print(f"Windows taskbar height: {WindowsUtils.get_windows_taskbar_height()}")

            x = screen_width - default_width - 5
            y = screen_height - default_height -  WindowsUtils.get_windows_taskbar_height()
            
            self.geometry(f"{default_width}x{default_height}+{x}+{y}")
        
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # Ensure window is visible
        self.deiconify()
        self.lift()
    
    def create_header(self):
        """Create menu header"""
        header_frame = tk.Frame(self.main_frame, bg=Colors.DARK_GREEN, height=30)
        header_frame.pack(fill=tk.X, padx=1, pady=1)
        header_frame.pack_propagate(False)
        
        # Make header draggable
        header_frame.bind("<Button-1>", self.start_drag)
        header_frame.bind("<B1-Motion>", self.do_drag)
        
        # Title
        title = tk.Label(header_frame, text="🪟 Windows Manager", 
                        bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                        font=Fonts.MENU_HEADER, cursor='fleur')
        title.pack(side=tk.LEFT, padx=10, pady=5)
        title.bind("<Button-1>", self.start_drag)
        title.bind("<B1-Motion>", self.do_drag)
        
        # Refresh button
        refresh_btn = tk.Button(header_frame, text="↻ Refresh", 
                               bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                               relief=tk.RAISED, bd=1, cursor='hand2',
                               font=Fonts.MENU_ITEM, command=self.refresh_window_list)
        refresh_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Close button
        close_btn = tk.Button(header_frame, text="X", 
                             bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                             relief=tk.RAISED, bd=1, cursor='hand2',
                             font=Fonts.MENU_ITEM, width=3,
                             command=self.close_window)
        close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def create_resize_handles(self):
        """Create resize handles for top, left, and right edges"""
        # Top resize handle
        top_handle = tk.Frame(self, cursor='size_ns', height=5)
        top_handle.place(relx=0.0, rely=0.0, relwidth=1.0, anchor='nw')
        top_handle.configure(bg=Colors.DARK_GREEN)
        
        # Bind resize events for top
        top_handle.bind("<Button-1>", lambda e: self.start_resize(e, 't'))
        top_handle.bind("<B1-Motion>", self.do_resize)
        top_handle.bind("<ButtonRelease-1>", self.end_resize)
        
        # Left resize handle
        left_handle = tk.Frame(self, cursor='size_we', width=5)
        left_handle.place(relx=0.0, rely=0.0, relheight=1.0, anchor='nw')
        left_handle.configure(bg=Colors.DARK_GREEN)
        
        # Bind resize events for left
        left_handle.bind("<Button-1>", lambda e: self.start_resize(e, 'l'))
        left_handle.bind("<B1-Motion>", self.do_resize)
        left_handle.bind("<ButtonRelease-1>", self.end_resize)
        
        # Right resize handle
        right_handle = tk.Frame(self, cursor='size_we', width=5)
        right_handle.place(relx=1.0, rely=0.0, relheight=1.0, anchor='ne')
        right_handle.configure(bg=Colors.DARK_GREEN)
        
        # Bind resize events for right
        right_handle.bind("<Button-1>", lambda e: self.start_resize(e, 'r'))
        right_handle.bind("<B1-Motion>", self.do_resize)
        right_handle.bind("<ButtonRelease-1>", self.end_resize)
        
        # Visual feedback on hover
        top_handle.bind("<Enter>", lambda e: self.configure(cursor='size_ns'))
        top_handle.bind("<Leave>", lambda e: self.configure(cursor=''))
        left_handle.bind("<Enter>", lambda e: self.configure(cursor='size_we'))
        left_handle.bind("<Leave>", lambda e: self.configure(cursor=''))
        right_handle.bind("<Enter>", lambda e: self.configure(cursor='size_we'))
        right_handle.bind("<Leave>", lambda e: self.configure(cursor=''))

    def start_drag(self, event):
        """Start dragging the window"""
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.original_x = self.winfo_x()
        self.original_y = self.winfo_y()

    def do_drag(self, event):
        """Handle window dragging"""
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y
        
        new_x = self.original_x + dx
        new_y = self.original_y + dy
        
        # Keep window on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        new_x = max(0, min(new_x, screen_width - window_width))
        new_y = max(0, min(new_y, screen_height - window_height))
        
        self.geometry(f"+{int(new_x)}+{int(new_y)}")
        
        # Update stored geometry in parent
        if hasattr(self.parent, 'windows_menu_geometry'):
            self.parent.windows_menu_geometry = self.get_current_geometry()
    
    def start_resize(self, event, edge):
        """Start resizing operation"""
        self.is_resizing = True
        self.resize_edge = edge
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        
        # Store original geometry
        self.original_geometry = {
            'x': self.winfo_x(),
            'y': self.winfo_y(),
            'width': self.winfo_width(),
            'height': self.winfo_height()
        }
        
        # Visual feedback
        self.main_frame.configure(relief=tk.SUNKEN)

    def do_resize(self, event):
        """Handle resize drag for all edges"""
        if not self.is_resizing or not self.resize_edge:
            return
        
        dx = event.x_root - self.resize_start_x
        dy = event.y_root - self.resize_start_y
        
        x = self.original_geometry['x']
        y = self.original_geometry['y']
        width = self.original_geometry['width']
        height = self.original_geometry['height']
        
        min_width = 400
        min_height = 300
        
        # Handle different edges
        if self.resize_edge == 't':  # Top edge
            new_height = max(min_height, height - dy)
            if new_height != height:
                y = y + (height - new_height)
                height = new_height
                
        elif self.resize_edge == 'l':  # Left edge
            new_width = max(min_width, width - dx)
            if new_width != width:
                x = x + (width - new_width)
                width = new_width
                
        elif self.resize_edge == 'r':  # Right edge
            new_width = max(min_width, width + dx)
            width = new_width
        
        # Apply new geometry
        self.geometry(f"{int(width)}x{int(height)}+{int(x)}+{int(y)}")

    def end_resize(self, event):
        """End resizing operation"""
        self.is_resizing = False
        self.resize_edge = None
        
        # Remove visual feedback
        self.main_frame.configure(relief=tk.RAISED)
        
        # Update stored geometry in parent
        if hasattr(self.parent, 'windows_menu_geometry'):
            self.parent.windows_menu_geometry = self.get_current_geometry()
            #print(f"Stored geometry after resize: {self.parent.windows_menu_geometry}")  # Debug
    
    def create_content_area(self):
        """Create scrollable content area with adjusted sizing"""
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.main_frame, bg=Colors.LIGHT_GREEN, 
                               highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", 
                                command=self.canvas.yview, width=12)  # Narrower scrollbar
        self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.LIGHT_GREEN)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def refresh_window_list(self):
        """Refresh the list of windows"""
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.window_items.clear()
        
        # Get current windows and filter out pinned ones
        all_windows = self.window_manager.get_relevant_windows()
        windows = [w for w in all_windows if not w.is_pinned]  # Exclude pinned windows
        
        if not windows:
            label = tk.Label(self.scrollable_frame, text="No unpinned windows found", 
                           bg=Colors.LIGHT_GREEN, fg=Colors.DARK_GREEN,
                           font=Fonts.MENU_ITEM)
            label.pack(pady=20)
            return
        
        # Create item for each window
        for window in windows:
            self.create_window_item(window)
    
    def create_window_item(self, window: ManagedWindow):
        """Create a single window item with colored pin button"""
        # Item container - make it more compact
        item_frame = tk.Frame(self.scrollable_frame, bg=Colors.LIGHT_GREEN, 
                             relief=tk.RAISED, bd=1, height=20)  # Fixed height
        item_frame.pack(fill=tk.X, padx=3, pady=1)  # Reduced padding
        #item_frame.pack_propagate(False)  # Prevent frame from resizing
        
        # # Pin button with app colors
        pin_btn = tk.Button(item_frame, text="Pin", 
                           bg=window.colors['bg'], fg=window.colors['fg'],
                           relief=tk.RAISED, bd=1, cursor='hand2',
                           font=('Arial', 8), width=4,  # Smaller font
                           command=lambda: self.toggle_pin(window))
        pin_btn.pack(side=tk.LEFT, padx=3, pady=2)
        
        # Window name label (without app prefix)
        label_bg = Colors.WINDOW_HIDDEN if window.is_hidden else Colors.WINDOW_VISIBLE
        label_fg = Colors.WHITE if window.is_hidden else Colors.BLACK
        
        # Use the display name which no longer has the app prefix
        display_text = window.display_name
        
        # Truncate very long names
        max_chars = 60
        if len(display_text) > max_chars:
            display_text = display_text[:max_chars-3] + "..."
        
        name_label = tk.Label(item_frame, text=display_text, 
                             bg=label_bg, fg=label_fg,
                             font=('Arial', 8), anchor='w',  # Smaller font
                             cursor='hand2', padx=5, pady=2)  # Reduced padding
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add subtle border on right side with app color
        color_indicator = tk.Frame(item_frame, bg=window.colors['bg'], width=3)
        color_indicator.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind click to toggle visibility
        name_label.bind("<Button-1>", lambda e: self.show_window(window))
        
        # Bind double click to close window
        name_label.bind("<Double-Button-1>", lambda e: self.remove_window(window))
        
        # Store references for updating
        self.window_items[window.hwnd] = {
            'frame': item_frame,
            'label': name_label,
            'pin_btn': pin_btn,
            'window': window
        }
    
    def toggle_window_visibility(self, window: ManagedWindow):
        """Toggle window visibility and update UI"""
        if self.window_manager.toggle_window_visibility(window):
            self.update_window_item(window)
    
    def show_window(self, window: ManagedWindow):
        """Show the window"""
        window.show()
        window.bring_to_front()

    
    def update_window_item(self, window: ManagedWindow):
        """Update the UI for a specific window item"""
        if window.hwnd not in self.window_items:
            return
        
        item = self.window_items[window.hwnd]
        
        # Update label color based on visibility
        label_bg = Colors.WINDOW_HIDDEN if window.is_hidden else Colors.WINDOW_VISIBLE
        label_fg = Colors.WHITE if window.is_hidden else Colors.BLACK
        item['label'].configure(bg=label_bg, fg=label_fg)

    # Close window and remove label button from windows_menu   
    def remove_window(self, window: ManagedWindow):
        """Close the window"""
        self.window_manager.close_managed_window(window)
        self.refresh_window_list()

    def toggle_pin(self, window: ManagedWindow):
        """Toggle window pin state"""
        print(f"\n=== TOGGLE PIN DEBUG ===")
        print(f"Window: {window.display_name}")
        print(f"Was pinned: {window.is_pinned}")
        
        if window.is_pinned:
            self.window_manager.unpin_window(window)
        else:
            self.window_manager.pin_window(window)
        
        print(f"Now pinned: {window.is_pinned}")
        
        # Notify callback to update taskbar
        if self.on_pin_callback:
            print(f"Calling on_pin_callback: {self.on_pin_callback}")
            self.on_pin_callback()
        else:
            print("ERROR: on_pin_callback is None!")
        
        # Remove this window from the list since it's now pinned
        if window.is_pinned:
            self.refresh_window_list()
        
        # List all pinned windows
        pinned = self.window_manager.get_pinned_windows()
        print(f"Total pinned windows: {len(pinned)}")
        for pw in pinned:
            print(f"  - {pw.display_name}")
        print("=== END DEBUG ===\n")
    
    def get_current_geometry(self):
        """Get current window geometry string"""
        return self.geometry()
    
    def close_window(self):
        """Close the windows menu"""
        # Store geometry before closing
        if hasattr(self.parent, 'windows_menu_geometry'):
            self.parent.stored_geometry = self.get_current_geometry()
            print(f"Storing geometry on close: {self.parent.windows_menu_geometry}")  # Debug
        
        # Unbind mousewheel to prevent errors
        self.canvas.unbind_all("<MouseWheel>")
        self.destroy()