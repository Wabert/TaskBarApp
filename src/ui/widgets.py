"""
Widget components for SuiteView Taskbar Application
"""
import tkinter as tk
from tkinter import ttk
from ..core.config import Colors, Fonts
from typing import Optional, Any, Dict, List


class FormField:
    """Form field wrapper for consistent styling"""
    
    def __init__(self, parent, label_text, field_type="entry", **kwargs):
        self.frame = tk.Frame(parent, bg=Colors.BG_PRIMARY)
        self.frame.pack(fill="x", pady=5)
        
        # Label
        self.label = tk.Label(self.frame, text=label_text, 
                            bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                            font=Fonts.DIALOG_BODY, width=15, anchor="w")
        self.label.pack(side=tk.LEFT)
        
        # Field
        if field_type == "entry":
            self.field = tk.Entry(self.frame, bg=Colors.BG_SECONDARY, 
                                fg=Colors.TEXT_PRIMARY, font=Fonts.DIALOG_BODY,
                                insertbackground=Colors.TEXT_PRIMARY, **kwargs)
        elif field_type == "text":
            self.field = tk.Text(self.frame, bg=Colors.BG_SECONDARY, 
                               fg=Colors.TEXT_PRIMARY, font=Fonts.DIALOG_BODY,
                               insertbackground=Colors.TEXT_PRIMARY, 
                               height=kwargs.get('height', 3), **kwargs)
        elif field_type == "combobox":
            self.field = ttk.Combobox(self.frame, **kwargs)
            self.field.configure(background=Colors.BG_SECONDARY, 
                               foreground=Colors.TEXT_PRIMARY)
        
        self.field.pack(side=tk.LEFT, fill="x", expand=True)
    
    def get(self):
        """Get field value"""
        if isinstance(self.field, tk.Text):
            return self.field.get("1.0", "end-1c")
        return self.field.get()
    
    def set(self, value):
        """Set field value"""
        if isinstance(self.field, tk.Text):
            self.field.delete("1.0", tk.END)
            self.field.insert("1.0", value)
        elif isinstance(self.field, tk.Entry):
            self.field.delete(0, tk.END)
            self.field.insert(0, value)
        elif isinstance(self.field, ttk.Combobox):
            self.field.set(value)
    
    def bind(self, event, handler):
        """Bind event to field"""
        self.field.bind(event, handler)
    
    def configure(self, **kwargs):
        """Configure field"""
        self.field.configure(**kwargs)
    
    def focus(self):
        """Set focus to field"""
        self.field.focus_set()
    
    def enable(self):
        """Enable field"""
        self.field.configure(state="normal")
    
    def disable(self):
        """Disable field"""
        self.field.configure(state="disabled")
    
    def readonly(self):
        """Make field readonly"""
        self.field.configure(state="readonly")


class CategoryHeader(tk.Frame):
    """Category header for grouped items"""
    
    def __init__(self, parent, text, bg_color=None):
        bg_color = bg_color or Colors.BG_TERTIARY
        super().__init__(parent, bg=bg_color, height=30)
        self.pack(fill="x", pady=(10, 5))
        
        label = tk.Label(self, text=text, bg=bg_color, fg=Colors.TEXT_PRIMARY,
                        font=Fonts.CATEGORY_HEADER)
        label.pack(side=tk.LEFT, padx=10)


class SectionDivider(tk.Frame):
    """Section divider line"""
    
    def __init__(self, parent, color=None, height=2):
        color = color or Colors.BORDER
        super().__init__(parent, bg=color, height=height)
        self.pack(fill="x", pady=10)


class ScrollableFrame(tk.Frame):
    """Scrollable frame container"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, bg=kwargs.get('bg', Colors.BG_PRIMARY),
                               highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", 
                                     command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, 
                                        bg=kwargs.get('bg', Colors.BG_PRIMARY))
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack widgets
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def get_frame(self):
        """Get the scrollable frame"""
        return self.scrollable_frame


class ToolTip:
    """Tooltip widget for hover help text"""
    
    def __init__(self, widget, text, delay=1000):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
        self.show_tooltip_job = None
    
    def on_enter(self, event=None):
        """Schedule tooltip display"""
        self.show_tooltip_job = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event=None):
        """Cancel tooltip display and hide if shown"""
        if self.show_tooltip_job:
            self.widget.after_cancel(self.show_tooltip_job)
            self.show_tooltip_job = None
        self.hide_tooltip()
    
    def show_tooltip(self):
        """Display the tooltip"""
        if self.tooltip or not self.text:
            return
        
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, justify=tk.LEFT,
                        bg=Colors.TOOLTIP_BG, fg=Colors.TOOLTIP_FG,
                        relief=tk.SOLID, borderwidth=1,
                        font=Fonts.TOOLTIP)
        label.pack()
    
    def hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class ButtonFactory:
    """Factory for creating consistent buttons"""
    
    @staticmethod
    def create_primary_button(parent, text, command, **kwargs):
        """Create a primary action button"""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=Colors.PRIMARY_GREEN,
            fg=Colors.TEXT_WHITE,
            activebackground=Colors.HOVER_GREEN,
            font=kwargs.get('font', Fonts.BUTTON_SMALL),
            relief=tk.FLAT,
            cursor='hand2',
            **{k: v for k, v in kwargs.items() if k not in ['bg', 'fg', 'font']}
        )
    
    @staticmethod
    def create_secondary_button(parent, text, command, **kwargs):
        """Create a secondary action button"""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.BG_TERTIARY,
            font=kwargs.get('font', Fonts.BUTTON_SMALL),
            relief=tk.FLAT,
            cursor='hand2',
            **{k: v for k, v in kwargs.items() if k not in ['bg', 'fg', 'font']}
        )
    
    @staticmethod
    def create_danger_button(parent, text, command, **kwargs):
        """Create a danger/destructive action button"""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=Colors.ERROR,
            fg=Colors.TEXT_WHITE,
            activebackground=Colors.ERROR_DARK,
            font=kwargs.get('font', Fonts.BUTTON_SMALL),
            relief=tk.FLAT,
            cursor='hand2',
            **{k: v for k, v in kwargs.items() if k not in ['bg', 'fg', 'font']}
        )
    
    @staticmethod
    def create_taskbar_button(parent, text, command, **kwargs):
        """Create a taskbar-style button"""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=Colors.DARK_GREEN,
            fg=Colors.WHITE,
            activebackground=Colors.HOVER_GREEN,
            font=Fonts.TASKBAR_BUTTON,
            relief=tk.FLAT,
            cursor='hand2',
            bd=0,
            padx=15,
            **{k: v for k, v in kwargs.items() if k not in ['bg', 'fg', 'font', 'relief', 'cursor', 'bd', 'padx']}
        )


class UIUtils:
    """Utility functions for UI operations"""
    
    @staticmethod
    def center_window(window, width=None, height=None):
        """Center a window on screen"""
        window.update_idletasks()
        
        # Get window size
        if width and height:
            window.geometry(f"{width}x{height}")
        else:
            width = window.winfo_width()
            height = window.winfo_height()
        
        # Calculate position
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def create_separator(parent, bg_color, width=2):
        """Create a vertical separator"""
        separator = tk.Frame(parent, bg=bg_color, width=width)
        return separator
    
    @staticmethod
    def bind_hover_effect(widget, hover_bg, normal_bg):
        """Bind hover effect to widget"""
        widget.bind("<Enter>", lambda e: widget.configure(bg=hover_bg))
        widget.bind("<Leave>", lambda e: widget.configure(bg=normal_bg))
    
    @staticmethod
    def create_styled_entry(parent, **kwargs):
        """Create a styled entry widget"""
        entry = tk.Entry(
            parent,
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            font=Fonts.DIALOG_BODY,
            relief=tk.FLAT,
            **kwargs
        )
        return entry
    
    @staticmethod
    def create_styled_text(parent, **kwargs):
        """Create a styled text widget"""
        text = tk.Text(
            parent,
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            font=Fonts.DIALOG_BODY,
            relief=tk.FLAT,
            wrap=tk.WORD,
            **kwargs
        )
        return text