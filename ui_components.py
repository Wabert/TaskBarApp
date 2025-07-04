# ui_components.py
"""
Shared UI components for SuiteView Taskbar Application
Contains reusable dialogs, custom widgets, and styling functions
Updated to use SimpleWindow
"""

import tkinter as tk
from tkinter import ttk
from config import Colors, Fonts, Dimensions
from utils import UIUtils
from simple_window_factory import SimpleWindow

class CustomDialog(SimpleWindow):
    """Base class for custom dialogs with consistent styling using SimpleWindow"""
    
    def __init__(self, parent, title, width=400, height=300, resizable=False, x=None, y=None):
        # Initialize SimpleWindow without resize handles
        super().__init__(parent, title, resize_handles=None)
        
        self.parent = parent
        self.result = None
        
        # Set window size
        self.geometry(f"{width}x{height}")
        
        # Set background color
        self.content_frame.configure(bg=Colors.LIGHT_GREEN)
        
        # Position window
        if x is not None and y is not None:
            self.geometry(f"{width}x{height}+{x}+{y}")
        else:
            # Center on parent
            self.update_idletasks()
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            x = parent_x + (parent_width - width) // 2
            y = parent_y + (parent_height - height) // 2
            self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Create dialog structure
        self._create_dialog_structure()
        
        # Pause parent's topmost maintenance if it has it
        if hasattr(parent, 'pause_topmost_maintenance'):
            parent.pause_topmost_maintenance()
        
        # Bind escape key
        self.bind('<Escape>', lambda e: self.cancel())
        
        # Focus
        self.focus_set()
    
    def _create_dialog_structure(self):
        """Create the standard dialog structure"""
        # Main content area - using the inherited content_frame
        self.dialog_content = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        self.dialog_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Button frame at bottom
        self.button_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        self.button_frame.pack(fill=tk.X, pady=(0, 20))
    
    def ok(self):
        """OK button clicked"""
        self.result = True
        self.destroy()
    
    def cancel(self):
        """Cancel button clicked"""
        self.result = None
        self.destroy()
    
    def destroy(self):
        """Override destroy to clean up properly"""
        # Resume parent's topmost maintenance
        if hasattr(self.parent, 'resume_topmost_maintenance'):
            self.parent.resume_topmost_maintenance()
        super().destroy()


class ConfirmationDialog(CustomDialog):
    """Confirmation dialog with Yes/No buttons"""
    
    def __init__(self, parent, title, message, icon="⚠️"):
        super().__init__(parent, title, width=350, height=200)
        
        # Icon and message
        icon_label = tk.Label(self.dialog_content, text=icon, bg=Colors.LIGHT_GREEN,
                             fg=Colors.BLACK, font=Fonts.WARNING_ICON)
        icon_label.pack(pady=10)
        
        message_label = tk.Label(self.dialog_content, text=message, bg=Colors.LIGHT_GREEN,
                               fg=Colors.BLACK, font=Fonts.DIALOG_LABEL, wraplength=300)
        message_label.pack(pady=5)
        
        # Buttons
        self.add_buttons()
        
        # Bind keys
        self.bind('<Return>', lambda e: self.yes())
        self.bind('<Escape>', lambda e: self.no())
    
    def add_buttons(self):
        """Add Yes/No buttons"""
        button_container = tk.Frame(self.button_frame, bg=Colors.LIGHT_GREEN)
        button_container.pack(expand=True)
        
        yes_btn = tk.Button(button_container, text="Yes", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                           command=self.yes, width=Dimensions.DIALOG_BUTTON_WIDTH,
                           font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        yes_btn.pack(side=tk.LEFT, padx=10)
        
        no_btn = tk.Button(button_container, text="No", bg=Colors.INACTIVE_GRAY, fg=Colors.WHITE,
                          command=self.no, width=Dimensions.DIALOG_BUTTON_WIDTH,
                          font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        no_btn.pack(side=tk.LEFT, padx=10)
        
        # Focus on No button (safer default)
        no_btn.focus_set()
    
    def yes(self):
        """Yes button clicked"""
        self.result = True
        self.destroy()
    
    def no(self):
        """No button clicked"""
        self.result = False
        self.destroy()
    
    @classmethod
    def ask(cls, parent, title, message, icon="⚠️"):
        """Show confirmation dialog and return result"""
        dialog = cls(parent, title, message, icon)
        dialog.lift()
        dialog.focus_force()
        parent.wait_window(dialog)
        return dialog.result


class LoadingDialog(SimpleWindow):
    """Simple loading dialog using SimpleWindow"""
    
    def __init__(self, parent, message="Loading..."):
        # Initialize SimpleWindow without resize handles
        super().__init__(parent, "Please Wait", resize_handles=None)
        
        # Set window size
        self.geometry("300x150")
        
        # Center on parent
        self.update_idletasks()
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 150) // 2
        self.geometry(f"300x150+{x}+{y}")
        
        # Set background color
        self.content_frame.configure(bg=Colors.LIGHT_GREEN)
        
        # Create content
        self.message = message
        self._create_content()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Start animation
        self.animate_progress()
    
    def _create_content(self):
        """Create the loading dialog content"""
        content = self.content_frame
        
        # Loading message
        self.msg_label = tk.Label(content, text=self.message,
                                 bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                                 font=Fonts.DIALOG_LABEL)
        self.msg_label.pack(pady=20)
        
        # Progress indicator (simple animation)
        self.progress_label = tk.Label(content, text="⏳",
                                      bg=Colors.LIGHT_GREEN, fg=Colors.DARK_GREEN,
                                      font=('Arial', 24))
        self.progress_label.pack(pady=10)
    
    def animate_progress(self):
        """Simple progress animation"""
        current = self.progress_label.cget("text")
        if current == "⏳":
            self.progress_label.config(text="⌛")
        else:
            self.progress_label.config(text="⏳")
        
        self.after(500, self.animate_progress)
    
    def update_message(self, new_message):
        """Update the loading message"""
        self.msg_label.config(text=new_message)


class WarningDialog(CustomDialog):
    """Warning dialog with OK button"""
    
    def __init__(self, parent, title, message, icon="⚠️"):
        super().__init__(parent, title, width=380, height=220)
        
        # Icon and message
        icon_label = tk.Label(self.dialog_content, text=icon, bg=Colors.LIGHT_GREEN,
                             fg=Colors.BLACK, font=('Arial', 24))
        icon_label.pack(pady=10)
        
        message_label = tk.Label(self.dialog_content, text=message, bg=Colors.LIGHT_GREEN,
                               fg=Colors.BLACK, font=Fonts.DIALOG_LABEL, wraplength=320)
        message_label.pack(pady=5)
        
        # Buttons
        self.add_buttons()
        
        # Bind keys
        self.bind('<Return>', lambda e: self.ok())
        self.bind('<Escape>', lambda e: self.ok())
    
    def add_buttons(self):
        """Add OK button"""
        button_container = tk.Frame(self.button_frame, bg=Colors.LIGHT_GREEN)
        button_container.pack(expand=True)
        
        ok_btn = tk.Button(button_container, text="OK", bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                          command=self.ok, width=Dimensions.DIALOG_BUTTON_WIDTH,
                          font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        ok_btn.pack(padx=10)
        ok_btn.focus_set()
    
    @classmethod
    def show(cls, parent, title, message, icon="⚠️"):
        """Show warning dialog"""
        dialog = cls(parent, title, message, icon)
        dialog.lift()
        dialog.focus_force()
        dialog.attributes('-topmost', True)
        parent.wait_window(dialog)
        return dialog.result


class ErrorDialog(CustomDialog):
    """Error dialog with OK button"""
    
    def __init__(self, parent, title, message, icon="❌"):
        super().__init__(parent, title, width=400, height=240)
        
        # Icon and message
        icon_label = tk.Label(self.dialog_content, text=icon, bg=Colors.LIGHT_GREEN,
                             fg=Colors.BLACK, font=('Arial', 24))
        icon_label.pack(pady=10)
        
        message_label = tk.Label(self.dialog_content, text=message, bg=Colors.LIGHT_GREEN,
                               fg=Colors.BLACK, font=Fonts.DIALOG_LABEL, wraplength=340)
        message_label.pack(pady=5)
        
        # Buttons
        self.add_buttons()
        
        # Bind keys
        self.bind('<Return>', lambda e: self.ok())
        self.bind('<Escape>', lambda e: self.ok())
    
    def add_buttons(self):
        """Add OK button"""
        button_container = tk.Frame(self.button_frame, bg=Colors.LIGHT_GREEN)
        button_container.pack(expand=True)
        
        ok_btn = tk.Button(button_container, text="OK", bg=Colors.INACTIVE_GRAY, fg=Colors.WHITE,
                          command=self.ok, width=Dimensions.DIALOG_BUTTON_WIDTH,
                          font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        ok_btn.pack(padx=10)
        ok_btn.focus_set()
    
    @classmethod
    def show(cls, parent, title, message, icon="❌"):
        """Show error dialog"""
        dialog = cls(parent, title, message, icon)
        dialog.lift()
        dialog.focus_force()
        dialog.attributes('-topmost', True)
        parent.wait_window(dialog)
        return dialog.result


# Helper Components (not dialogs, so don't change these)

class FormField:
    """Helper class for creating form fields with clipboard support"""
    
    def __init__(self, parent, label_text, field_type='entry', layout='side-by-side', **kwargs):
        self.frame = tk.Frame(parent, bg=Colors.LIGHT_GREEN)
        self.layout = layout
        
        if layout == 'stacked':
            # Label on top, widget below
            self.label = tk.Label(self.frame, text=label_text, bg=Colors.LIGHT_GREEN, 
                                fg=Colors.BLACK, font=Fonts.DIALOG_LABEL)
            self.label.pack(anchor='w', pady=(0, 2))
            
            if field_type == 'entry':
                self.widget = tk.Entry(self.frame, font=Fonts.DIALOG_LABEL, **kwargs)
                self._bind_clipboard_operations()
            elif field_type == 'combobox':
                self.widget = ttk.Combobox(self.frame, font=Fonts.DIALOG_LABEL, **kwargs)
                self._bind_combobox_clipboard_operations()
            elif field_type == 'text':
                self.widget = tk.Text(self.frame, font=Fonts.DIALOG_LABEL, **kwargs)
                self._bind_text_clipboard_operations()
            
            self.widget.pack(fill=tk.X)
        else:
            # Side-by-side layout
            self.label = tk.Label(self.frame, text=label_text, bg=Colors.LIGHT_GREEN, 
                                fg=Colors.BLACK, font=Fonts.DIALOG_LABEL)
            self.label.pack(side=tk.LEFT, padx=(0, 10))
            
            if field_type == 'entry':
                self.widget = tk.Entry(self.frame, font=Fonts.DIALOG_LABEL, **kwargs)
                self._bind_clipboard_operations()
            elif field_type == 'combobox':
                self.widget = ttk.Combobox(self.frame, font=Fonts.DIALOG_LABEL, **kwargs)
                self._bind_combobox_clipboard_operations()
            elif field_type == 'text':
                self.widget = tk.Text(self.frame, font=Fonts.DIALOG_LABEL, **kwargs)
                self._bind_text_clipboard_operations()
            
            self.widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _bind_clipboard_operations(self):
        """Bind standard clipboard operations for Entry widgets"""
        self.widget.bind('<Control-a>', lambda e: self.widget.select_range(0, 'end'))
        self.widget.bind('<Control-A>', lambda e: self.widget.select_range(0, 'end'))
        # Ctrl+C and Ctrl+V are automatically handled by tkinter Entry
    
    def _bind_combobox_clipboard_operations(self):
        """Bind clipboard operations for Combobox widgets"""
        # Combobox uses an internal Entry widget
        self.widget.bind('<Control-a>', lambda e: self.widget.event_generate('<<SelectAll>>'))
        self.widget.bind('<Control-A>', lambda e: self.widget.event_generate('<<SelectAll>>'))
    
    def _bind_text_clipboard_operations(self):
        """Bind clipboard operations for Text widgets"""
        self.widget.bind('<Control-a>', lambda e: self.widget.tag_add('sel', '1.0', 'end'))
        self.widget.bind('<Control-A>', lambda e: self.widget.tag_add('sel', '1.0', 'end'))
    
    def pack(self, **kwargs):
        """Pack the form field frame"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the form field frame"""
        self.frame.grid(**kwargs)
    
    def get(self):
        """Get the widget value"""
        if isinstance(self.widget, tk.Text):
            return self.widget.get('1.0', 'end-1c')
        else:
            return self.widget.get()
    
    def set(self, value):
        """Set the widget value"""
        if isinstance(self.widget, tk.Text):
            self.widget.delete('1.0', 'end')
            self.widget.insert('1.0', value)
        elif isinstance(self.widget, ttk.Combobox):
            self.widget.set(value)
        else:
            self.widget.delete(0, 'end')
            self.widget.insert(0, value)
    
    def focus_set(self):
        """Set focus to the widget"""
        self.widget.focus_set()


class CategoryHeader(tk.Frame):
    """Styled category header for menus and dialogs"""
    
    def __init__(self, parent, text, bg_color=Colors.DARK_GREEN, fg_color=Colors.WHITE):
        super().__init__(parent, bg=bg_color, height=25)
        self.pack_propagate(False)
        
        self.label = tk.Label(self, text=text, bg=bg_color, fg=fg_color,
                             font=Fonts.MENU_HEADER, anchor='w')
        self.label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)


class SectionDivider(tk.Frame):
    """Horizontal divider for visual separation"""
    
    def __init__(self, parent, color=Colors.MEDIUM_GREEN, height=2):
        super().__init__(parent, bg=color, height=height)


class ScrollableFrame(tk.Frame):
    """Frame with scrollbar support"""
    
    def __init__(self, parent, bg_color=Colors.LIGHT_GREEN, **kwargs):
        container = tk.Frame(parent, bg=bg_color)
        container.pack(fill=tk.BOTH, expand=True, **kwargs)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(container, bg=bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        # Create the scrollable frame
        super().__init__(self.canvas, bg=bg_color)
        self.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Store reference to canvas
        self.parent_canvas = self.canvas
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def update_scroll_region(self):
        """Update the scroll region to encompass all widgets"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class ToolTip:
    """Simple tooltip implementation"""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Show the tooltip"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, bg=Colors.LIGHT_GREEN,
                        fg=Colors.BLACK, relief=tk.SOLID, borderwidth=1,
                        font=("Arial", 9))
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide the tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


# Utility functions

class UIUtils:
    """Static utility methods for UI operations"""
    
    @staticmethod
    def center_window(window, width=None, height=None):
        """Center a window on screen"""
        window.update_idletasks()
        
        # Get window size
        if width is None:
            width = window.winfo_width()
        if height is None:
            height = window.winfo_height()
        
        # Calculate position
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def create_hover_effect(widget, enter_bg, leave_bg, enter_fg=None, leave_fg=None):
        """Create hover effect for a widget"""
        def on_enter(event):
            widget.config(bg=enter_bg)
            if enter_fg:
                widget.config(fg=enter_fg)
        
        def on_leave(event):
            widget.config(bg=leave_bg)
            if leave_fg:
                widget.config(fg=leave_fg)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
        return on_enter, on_leave
    
    @staticmethod
    def create_separator(parent, bg_color, width=2):
        """Create a vertical separator"""
        import tkinter as tk
        separator = tk.Frame(parent, bg=bg_color, width=width)
        return separator