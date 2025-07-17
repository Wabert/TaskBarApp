"""
Dialog components for SuiteView Taskbar Application
"""
import tkinter as tk
from tkinter import ttk
from .window_base import SimpleWindow
from ..core.config import Colors, Fonts, DialogSizes
from typing import Optional, Callable


class DialogBase(SimpleWindow):
    """Base class for all dialog windows with common functionality"""
    
    def __init__(self, parent=None, title="Dialog", width=None, height=None):
        width = width or DialogSizes.SMALL[0]
        height = height or DialogSizes.SMALL[1]
        super().__init__(parent, title, width, height)
        self.result = None
        self.parent = parent
        
        # Configure base style
        self.root.configure(bg=Colors.BG_PRIMARY)
        
        # Make dialog modal
        if parent:
            self.root.transient(parent)
            self.root.grab_set()
        
        # Bind escape key to cancel
        self.root.bind("<Escape>", lambda e: self.cancel())
        
        # Center the dialog
        self.center_on_parent()
    
    def center_on_parent(self):
        """Center dialog on parent window or screen"""
        self.root.update_idletasks()
        
        if self.parent:
            # Get parent window position and size
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            # Calculate center position
            x = parent_x + (parent_width - self.root.winfo_width()) // 2
            y = parent_y + (parent_height - self.root.winfo_height()) // 2
        else:
            # Center on screen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - self.root.winfo_width()) // 2
            y = (screen_height - self.root.winfo_height()) // 2
        
        self.root.geometry(f"+{x}+{y}")
    
    def create_button_frame(self) -> tk.Frame:
        """Create standard button frame for OK/Cancel buttons"""
        button_frame = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        return button_frame
    
    def ok(self, result=True):
        """Handle OK button click"""
        self.result = result
        self.close()
    
    def cancel(self):
        """Handle Cancel button click"""
        self.result = None
        self.close()
    
    def show(self):
        """Show dialog and wait for result"""
        self.root.wait_window()
        return self.result


class CustomDialog(DialogBase):
    """Custom dialog with configurable content"""
    
    def __init__(self, parent=None, title="Dialog", width=None, height=None):
        super().__init__(parent, title, width, height)
        
        # Content area for subclasses
        self.dialog_content = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY)
        self.dialog_content.pack(fill="both", expand=True, padx=20, pady=20)


class ConfirmationDialog(CustomDialog):
    """Confirmation dialog with Yes/No options"""
    
    def __init__(self, parent=None, title="Confirm", message="Are you sure?", width=400, height=150):
        super().__init__(parent, title, width, height)
        
        # Message
        self.message_label = tk.Label(self.dialog_content, text=message,
                                    bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                                    font=Fonts.DIALOG_BODY, wraplength=350,
                                    justify=tk.CENTER)
        self.message_label.pack(pady=20)
        
        # Buttons
        button_frame = self.create_button_frame()
        
        self.yes_button = tk.Button(button_frame, text="Yes", 
                                  bg=Colors.PRIMARY_GREEN, fg=Colors.TEXT_WHITE,
                                  font=Fonts.BUTTON_SMALL, width=10,
                                  command=lambda: self.ok(True))
        self.yes_button.pack(side=tk.RIGHT, padx=5)
        
        self.no_button = tk.Button(button_frame, text="No",
                                 bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY,
                                 font=Fonts.BUTTON_SMALL, width=10,
                                 command=lambda: self.ok(False))
        self.no_button.pack(side=tk.RIGHT, padx=5)
        
        # Focus on No button by default for safety
        self.no_button.focus_set()


class LoadingDialog(SimpleWindow):
    """Loading dialog with progress display"""
    
    def __init__(self, parent=None, title="Loading", message="Please wait...", width=300, height=150):
        super().__init__(parent, title, width, height)
        
        self.root.configure(bg=Colors.BG_PRIMARY)
        
        # Make modal
        if parent:
            self.root.transient(parent)
            self.root.grab_set()
        
        # Message
        self.message_label = tk.Label(self.content_frame, text=message,
                                    bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                                    font=Fonts.DIALOG_BODY)
        self.message_label.pack(pady=20)
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar",
                       background=Colors.PRIMARY_GREEN,
                       troughcolor=Colors.BG_SECONDARY,
                       bordercolor=Colors.BORDER,
                       lightcolor=Colors.PRIMARY_GREEN,
                       darkcolor=Colors.DARK_GREEN)
        
        self.progress = ttk.Progressbar(self.content_frame, 
                                      style="Custom.Horizontal.TProgressbar",
                                      mode='indeterminate', 
                                      length=200)
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Center on parent
        self.center_on_parent()
    
    def center_on_parent(self):
        """Center dialog on parent window"""
        self.root.update_idletasks()
        
        if hasattr(self, 'parent') and self.parent:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            x = parent_x + (parent_width - self.root.winfo_width()) // 2
            y = parent_y + (parent_height - self.root.winfo_height()) // 2
            
            self.root.geometry(f"+{x}+{y}")
    
    def update_message(self, message):
        """Update the loading message"""
        self.message_label.config(text=message)
        self.root.update()
    
    def close(self):
        """Stop progress and close dialog"""
        self.progress.stop()
        super().close()


class WarningDialog(CustomDialog):
    """Warning dialog with custom icon and message"""
    
    def __init__(self, parent=None, title="Warning", message="Warning!", width=400, height=200):
        super().__init__(parent, title, width, height)
        
        # Warning icon (using text for simplicity)
        icon_label = tk.Label(self.dialog_content, text="⚠",
                            bg=Colors.BG_PRIMARY, fg=Colors.WARNING,
                            font=("Arial", 32))
        icon_label.pack(pady=(0, 10))
        
        # Message
        self.message_label = tk.Label(self.dialog_content, text=message,
                                    bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                                    font=Fonts.DIALOG_BODY, wraplength=350,
                                    justify=tk.CENTER)
        self.message_label.pack(pady=(0, 20))
        
        # OK button
        button_frame = self.create_button_frame()
        self.ok_button = tk.Button(button_frame, text="OK",
                                 bg=Colors.PRIMARY_GREEN, fg=Colors.TEXT_WHITE,
                                 font=Fonts.BUTTON_SMALL, width=10,
                                 command=self.ok)
        self.ok_button.pack()
        self.ok_button.focus_set()


class ErrorDialog(CustomDialog):
    """Error dialog with custom icon and message"""
    
    def __init__(self, parent=None, title="Error", message="An error occurred", width=400, height=200):
        super().__init__(parent, title, width, height)
        
        # Error icon (using text for simplicity)
        icon_label = tk.Label(self.dialog_content, text="❌",
                            bg=Colors.BG_PRIMARY, fg=Colors.ERROR,
                            font=("Arial", 32))
        icon_label.pack(pady=(0, 10))
        
        # Message
        self.message_label = tk.Label(self.dialog_content, text=message,
                                    bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                                    font=Fonts.DIALOG_BODY, wraplength=350,
                                    justify=tk.CENTER)
        self.message_label.pack(pady=(0, 20))
        
        # OK button
        button_frame = self.create_button_frame()
        self.ok_button = tk.Button(button_frame, text="OK",
                                 bg=Colors.PRIMARY_GREEN, fg=Colors.TEXT_WHITE,
                                 font=Fonts.BUTTON_SMALL, width=10,
                                 command=self.ok)
        self.ok_button.pack()
        self.ok_button.focus_set()


class FilterMenuDialog(SimpleWindow):
    """Dialog for filtering menu items"""
    
    def __init__(self, parent, title="Filter Menu", menu_items=None, current_filter=None):
        super().__init__(parent, title, DialogSizes.MEDIUM[0], DialogSizes.MEDIUM[1])
        
        self.parent_window = parent
        self.menu_items = menu_items or []
        self.current_filter = current_filter or {"apps": set(), "categories": set()}
        self.temp_filter = {"apps": set(self.current_filter["apps"]), 
                           "categories": set(self.current_filter["categories"])}
        
        self.root.configure(bg=Colors.BG_PRIMARY)
        self.create_widgets()
        
        # Make modal
        self.root.transient(parent)
        self.root.grab_set()
        
        # Center on parent
        self.center_on_parent()
    
    def center_on_parent(self):
        """Center dialog on parent window"""
        self.root.update_idletasks()
        parent_x = self.parent_window.winfo_x()
        parent_y = self.parent_window.winfo_y()
        parent_width = self.parent_window.winfo_width()
        parent_height = self.parent_window.winfo_height()
        
        x = parent_x + (parent_width - self.root.winfo_width()) // 2
        y = parent_y + (parent_height - self.root.winfo_height()) // 2
        
        self.root.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create filter dialog widgets"""
        # Header
        header = tk.Label(self.content_frame, text="Select items to show:",
                         bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                         font=Fonts.DIALOG_HEADER)
        header.pack(pady=(10, 20))
        
        # Main container with two columns
        main_container = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY)
        main_container.pack(fill="both", expand=True, padx=20)
        
        # Apps column
        apps_frame = tk.Frame(main_container, bg=Colors.BG_PRIMARY)
        apps_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10))
        
        apps_label = tk.Label(apps_frame, text="Applications",
                             bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                             font=Fonts.DIALOG_BODY)
        apps_label.pack()
        
        # Apps checkboxes with scrollbar
        apps_scroll_frame = tk.Frame(apps_frame, bg=Colors.BG_PRIMARY)
        apps_scroll_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        apps_canvas = tk.Canvas(apps_scroll_frame, bg=Colors.BG_PRIMARY,
                               highlightthickness=0, width=200)
        apps_scrollbar = tk.Scrollbar(apps_scroll_frame, orient="vertical",
                                     command=apps_canvas.yview)
        self.apps_inner_frame = tk.Frame(apps_canvas, bg=Colors.BG_PRIMARY)
        
        apps_canvas.configure(yscrollcommand=apps_scrollbar.set)
        apps_canvas_window = apps_canvas.create_window((0, 0), window=self.apps_inner_frame,
                                                      anchor="nw")
        
        apps_canvas.pack(side=tk.LEFT, fill="both", expand=True)
        apps_scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # Get unique apps
        apps = set()
        for item in self.menu_items:
            if hasattr(item, 'app'):
                apps.add(item.app)
        
        self.app_vars = {}
        for app in sorted(apps):
            var = tk.BooleanVar(value=app not in self.temp_filter["apps"])
            self.app_vars[app] = var
            
            cb = tk.Checkbutton(self.apps_inner_frame, text=app, variable=var,
                               bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                               selectcolor=Colors.BG_SECONDARY,
                               activebackground=Colors.BG_PRIMARY,
                               font=Fonts.MENU_ITEM)
            cb.pack(anchor="w", pady=2)
        
        # Update scroll region
        self.apps_inner_frame.update_idletasks()
        apps_canvas.configure(scrollregion=apps_canvas.bbox("all"))
        
        # Categories column
        cats_frame = tk.Frame(main_container, bg=Colors.BG_PRIMARY)
        cats_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(10, 0))
        
        cats_label = tk.Label(cats_frame, text="Categories",
                             bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                             font=Fonts.DIALOG_BODY)
        cats_label.pack()
        
        # Categories checkboxes with scrollbar
        cats_scroll_frame = tk.Frame(cats_frame, bg=Colors.BG_PRIMARY)
        cats_scroll_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        cats_canvas = tk.Canvas(cats_scroll_frame, bg=Colors.BG_PRIMARY,
                               highlightthickness=0, width=200)
        cats_scrollbar = tk.Scrollbar(cats_scroll_frame, orient="vertical",
                                     command=cats_canvas.yview)
        self.cats_inner_frame = tk.Frame(cats_canvas, bg=Colors.BG_PRIMARY)
        
        cats_canvas.configure(yscrollcommand=cats_scrollbar.set)
        cats_canvas_window = cats_canvas.create_window((0, 0), window=self.cats_inner_frame,
                                                       anchor="nw")
        
        cats_canvas.pack(side=tk.LEFT, fill="both", expand=True)
        cats_scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # Get unique categories
        categories = set()
        for item in self.menu_items:
            if hasattr(item, 'category'):
                categories.add(item.category)
        
        self.category_vars = {}
        for category in sorted(categories):
            var = tk.BooleanVar(value=category not in self.temp_filter["categories"])
            self.category_vars[category] = var
            
            cb = tk.Checkbutton(self.cats_inner_frame, text=category, variable=var,
                               bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                               selectcolor=Colors.BG_SECONDARY,
                               activebackground=Colors.BG_PRIMARY,
                               font=Fonts.MENU_ITEM)
            cb.pack(anchor="w", pady=2)
        
        # Update scroll region
        self.cats_inner_frame.update_idletasks()
        cats_canvas.configure(scrollregion=cats_canvas.bbox("all"))
        
        # Select/Deselect all buttons
        select_frame = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY)
        select_frame.pack(fill="x", pady=10)
        
        select_all_btn = tk.Button(select_frame, text="Select All",
                                 bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY,
                                 font=Fonts.BUTTON_SMALL,
                                 command=lambda: self.select_all(True))
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        deselect_all_btn = tk.Button(select_frame, text="Deselect All",
                                    bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY,
                                    font=Fonts.BUTTON_SMALL,
                                    command=lambda: self.select_all(False))
        deselect_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY)
        button_frame.pack(side=tk.BOTTOM, fill="x", pady=10)
        
        self.apply_button = tk.Button(button_frame, text="Apply",
                                    bg=Colors.PRIMARY_GREEN, fg=Colors.TEXT_WHITE,
                                    font=Fonts.BUTTON_SMALL, width=10,
                                    command=self.apply_filter)
        self.apply_button.pack(side=tk.RIGHT, padx=5)
        
        self.cancel_button = tk.Button(button_frame, text="Cancel",
                                     bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY,
                                     font=Fonts.BUTTON_SMALL, width=10,
                                     command=self.close)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        
        self.reset_button = tk.Button(button_frame, text="Reset",
                                    bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY,
                                    font=Fonts.BUTTON_SMALL, width=10,
                                    command=self.reset_filter)
        self.reset_button.pack(side=tk.LEFT, padx=5)
    
    def select_all(self, select=True):
        """Select or deselect all items"""
        for var in self.app_vars.values():
            var.set(select)
        for var in self.category_vars.values():
            var.set(select)
    
    def reset_filter(self):
        """Reset filter to show all items"""
        self.select_all(True)
    
    def apply_filter(self):
        """Apply the selected filter"""
        # Build filter from unchecked items
        self.current_filter["apps"] = {app for app, var in self.app_vars.items() 
                                      if not var.get()}
        self.current_filter["categories"] = {cat for cat, var in self.category_vars.items() 
                                           if not var.get()}
        
        # Notify parent window
        if hasattr(self.parent_window, 'apply_filter'):
            self.parent_window.apply_filter(self.current_filter)
        
        self.close()