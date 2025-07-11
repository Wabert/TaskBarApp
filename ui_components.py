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

class FilterMenuDialog(SimpleWindow):
    """Dialog for selecting filter values for a column"""
    
    def __init__(self, parent, column_key, column_header, unique_values, current_selection, apply_callback):
        super().__init__(parent, f"Filter: {column_header}", resize_handles=None)
        
        # Set window size
        self.geometry("350x400")
        
        # Center on parent
        self.update_idletasks()
        if parent:
            parent.update_idletasks()
            x = parent.winfo_x() + (parent.winfo_width() - 350) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 400) // 2
            self.geometry(f"350x400+{x}+{y}")
        
        # Set background color
        self.content_frame.configure(bg=Colors.LIGHT_GREEN)
        
        self.column_key = column_key
        self.column_header = column_header
        self.unique_values = unique_values
        self.current_selection = current_selection.copy()
        self.apply_callback = apply_callback
        self.parent_window = parent
        
        # Check if filter exists
        self.has_existing_filter = column_key in parent.active_filters
        
        # Default to all selected if no current selection
        if not self.current_selection and not self.has_existing_filter:
            self.current_selection = set(unique_values)
        
        self.create_filter_interface()
        self.create_action_buttons()
    
    def create_filter_interface(self):
        """Create the filter selection interface"""
        # Clear Filter button
        if self.has_existing_filter:
            clear_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
            clear_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
            
            clear_filter_btn = tk.Button(clear_frame, text="Clear Filter for This Column", 
                                       bg=Colors.INACTIVE_GRAY, fg=Colors.WHITE,
                                       command=self.clear_column_filter, 
                                       font=Fonts.DIALOG_LABEL,
                                       cursor='hand2', relief=tk.RAISED, bd=1)
            clear_filter_btn.pack(pady=5)
        
        # Search box
        search_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        search_frame.pack(fill=tk.X, pady=5, padx=10)
        
        tk.Label(search_frame, text="Search:", bg=Colors.LIGHT_GREEN, 
                fg=Colors.BLACK, font=Fonts.DIALOG_LABEL).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_list)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=Fonts.DIALOG_LABEL)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Select All / None buttons
        select_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        select_frame.pack(fill=tk.X, pady=5, padx=10)
        
        select_all_btn = tk.Button(select_frame, text="Select All", 
                                  bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                                  command=self.select_all, font=Fonts.DIALOG_LABEL)
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        select_none_btn = tk.Button(select_frame, text="Select None", 
                                   bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                                   command=self.select_none, font=Fonts.DIALOG_LABEL)
        select_none_btn.pack(side=tk.LEFT, padx=5)
        
        # Listbox with checkboxes
        list_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        self.filter_tree = ttk.Treeview(list_frame, show='tree', height=12)
        self.filter_tree.column('#0', width=300)
        
        filter_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                        command=self.filter_tree.yview)
        self.filter_tree.configure(yscrollcommand=filter_scrollbar.set)
        
        self.filter_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        filter_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.populate_filter_list()
        
        # Bind click events
        self.filter_tree.bind('<Button-1>', self.on_click)
        self.filter_tree.bind('<Return>', self.toggle_item)
    
    def clear_column_filter(self):
        """Clear the filter for this specific column"""
        self.apply_callback(self.column_key, [])
        self.close_window()
    
    def on_click(self, event):
        """Handle click on items"""
        item = self.filter_tree.identify('item', event.x, event.y)
        if item:
            self.filter_tree.selection_set(item)
            self.toggle_item()
    
    def populate_filter_list(self, search_text=""):
        """Populate the filter list"""
        for item in self.filter_tree.get_children():
            self.filter_tree.delete(item)
        
        filtered_values = [val for val in self.unique_values 
                          if search_text.lower() in val.lower()] if search_text else self.unique_values
        
        for value in filtered_values:
            checkbox = "☑" if value in self.current_selection else "☐"
            display_text = f"{checkbox} {value}"
            self.filter_tree.insert('', 'end', text=display_text, values=[value])
    
    def filter_list(self, *args):
        """Filter the list based on search"""
        self.populate_filter_list(self.search_var.get())
    
    def toggle_item(self, event=None):
        """Toggle selection of an item"""
        selected_item = self.filter_tree.selection()
        if not selected_item:
            return
        
        item_id = selected_item[0]
        values = self.filter_tree.item(item_id, 'values')
        if values:
            value = values[0]
            
            if value in self.current_selection:
                self.current_selection.remove(value)
            else:
                self.current_selection.add(value)
            
            self.populate_filter_list(self.search_var.get())
    
    def select_all(self):
        """Select all visible items"""
        search_text = self.search_var.get()
        filtered_values = [val for val in self.unique_values 
                          if search_text.lower() in val.lower()] if search_text else self.unique_values
        
        for value in filtered_values:
            self.current_selection.add(value)
        
        self.populate_filter_list(search_text)
    
    def select_none(self):
        """Deselect all visible items"""
        search_text = self.search_var.get()
        filtered_values = [val for val in self.unique_values 
                          if search_text.lower() in val.lower()] if search_text else self.unique_values
        
        for value in filtered_values:
            self.current_selection.discard(value)
        
        self.populate_filter_list(search_text)
    
    def create_action_buttons(self):
        """Create OK and Cancel buttons"""
        button_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        button_frame.pack(side=tk.BOTTOM, pady=10, padx=10)
        
        button_container = tk.Frame(button_frame, bg=Colors.LIGHT_GREEN)
        button_container.pack()
        
        ok_btn = tk.Button(button_container, text="OK", 
                          bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                          command=self.apply_filter, width=Dimensions.DIALOG_BUTTON_WIDTH,
                          font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        ok_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_container, text="Cancel", 
                              bg=Colors.INACTIVE_GRAY, fg=Colors.WHITE,
                              command=self.cancel, width=Dimensions.DIALOG_BUTTON_WIDTH,
                              font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        ok_btn.focus_set()
    
    def apply_filter(self):
        """Apply the selected filter"""
        self.apply_callback(self.column_key, list(self.current_selection))
        self.close_window()
    
    def cancel(self):
        """Cancel without applying changes"""
        self.close_window()


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

class FilterView(tk.Frame):
    """
    Reusable interactive frame for viewing any tabular data with Excel-like filtering
    Inherits from tk.Frame for embedding in other windows
    
    Args:
        parent: Parent frame/window to populate
        data: List of dictionaries containing the data to display
        columns: List of column configurations, each with:
            - key: Dictionary key for this column
            - header: Display name for column header
            - width: Column width (default: 100)
            - type: Data type ('text', 'number', 'date') for sorting (default: 'text')
        on_item_click: Callback function(item) when item is clicked
        on_item_double_click: Callback function(item) when item is double-clicked
    """
    
    def __init__(self, parent, data, columns=None, on_item_click=None, on_item_double_click=None):
        # Initialize Frame
        super().__init__(parent, bg=Colors.LIGHT_GREEN)
        
        # Store data
        self.original_data = data.copy() if data else []
        self.filtered_data = self.original_data.copy()
        
        # Configuration
        self.column_configs = columns or self._auto_generate_columns()
        self.on_item_click = on_item_click
        self.on_item_double_click = on_item_double_click
        
        # Extract column information
        self.columns = [col['key'] for col in self.column_configs]
        self.column_headers = {col['key']: col.get('header', col['key']) for col in self.column_configs}
        self.column_widths = {col['key']: col.get('width', 100) for col in self.column_configs}
        self.column_types = {col['key']: col.get('type', 'text') for col in self.column_configs}
        
        # Filter state tracking
        self.active_filters = {}
        self.column_unique_values = {}
        
        # Create UI components
        self.create_data_grid()
        
        # Populate
        self.populate_grid()
        
        # Expose the tree object
        self.tree = self.data_tree
        
    def _auto_generate_columns(self):
        """Auto-generate column configuration from data"""
        if not self.original_data:
            return []
        
        # Get all unique keys from data
        all_keys = set()
        for item in self.original_data:
            all_keys.update(item.keys())
        
        # Create column config for each key
        columns = []
        for key in sorted(all_keys):
            columns.append({
                'key': key,
                'header': key.replace('_', ' ').title(),
                'width': 150,
                'type': self._guess_column_type(key)
            })
        
        return columns
    
    def _guess_column_type(self, key):
        """Guess column type based on key name and sample data"""
        key_lower = key.lower()
        
        # Check key name patterns
        if any(word in key_lower for word in ['date', 'time', 'created', 'modified', 'updated']):
            return 'date'
        elif any(word in key_lower for word in ['count', 'number', 'size', 'bytes', 'id', 'qty', 'quantity']):
            return 'number'
        
        # Check sample data
        sample_values = []
        for item in self.original_data[:10]:  # Check first 10 items
            if key in item and item[key] is not None:
                sample_values.append(item[key])
        
        if sample_values:
            # Check if all values are numeric
            try:
                for val in sample_values:
                    float(str(val).replace(',', ''))
                return 'number'
            except:
                pass
        
        return 'text'
    
    def create_data_grid(self):
        """Create the main data grid with filtering"""
        grid_frame = tk.Frame(self, bg=Colors.LIGHT_GREEN, relief=tk.SUNKEN, bd=1)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Create Treeview
        self.data_tree = ttk.Treeview(grid_frame, show='tree headings')
        self.data_tree['columns'] = self.columns
        
        # Configure columns
        self.data_tree.column('#0', width=0, stretch=False)
        self.data_tree.heading('#0', text='')
        
        for col in self.columns:
            self.data_tree.column(col, width=self.column_widths.get(col, 100), anchor='w')
            header_text = self.column_headers.get(col, col)
            self.data_tree.heading(col, text=header_text, command=lambda c=col: self.show_filter_menu(c))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        h_scrollbar = ttk.Scrollbar(grid_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack components
        self.data_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(0, weight=1)
        
        # Style
        style = ttk.Style()
        style.configure('Treeview', background=Colors.LIGHT_GREEN, 
                       foreground=Colors.BLACK, fieldbackground=Colors.LIGHT_GREEN)
        style.configure('Treeview.Heading', background=Colors.MEDIUM_GREEN,
                       foreground=Colors.WHITE, font=Fonts.MENU_HEADER)
        
        # Bind click events
        if self.on_item_click:
            self.data_tree.bind('<ButtonRelease-1>', self._handle_item_click)
        if self.on_item_double_click:
            self.data_tree.bind('<Double-Button-1>', self._handle_item_double_click)
    
    def _handle_item_click(self, event):
        """Handle single click on item with column detection"""
        selection = self.data_tree.selection()
        if selection and self.on_item_click:
            item_id = selection[0]
            item_index = self.data_tree.index(item_id)
            
            if 0 <= item_index < len(self.filtered_data):
                # Determine which column was clicked
                column_id = self.data_tree.identify_column(event.x)
                
                # Convert column id (#1, #2, etc.) to column index
                if column_id:
                    try:
                        col_index = int(column_id.replace('#', '')) - 1
                        if 0 <= col_index < len(self.columns):
                            column_key = self.columns[col_index]
                            # Pass both item and column to callback
                            if hasattr(self.on_item_click, '__code__') and self.on_item_click.__code__.co_argcount > 2:
                                # New style callback with column info
                                self.on_item_click(self.filtered_data[item_index], column_key)
                            else:
                                # Old style callback without column info
                                self.on_item_click(self.filtered_data[item_index])
                    except:
                        # Fallback to just item
                        self.on_item_click(self.filtered_data[item_index])
    
    def _handle_item_double_click(self, event):
        """Handle double click on item"""
        selection = self.data_tree.selection()
        if selection and self.on_item_double_click:
            item_id = selection[0]
            item_index = self.data_tree.index(item_id)
            if 0 <= item_index < len(self.filtered_data):
                self.on_item_double_click(self.filtered_data[item_index])
    
    def populate_grid(self):
        """Populate the grid with current filtered data"""
        # Clear existing items
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Add filtered data
        for item in self.filtered_data:
            values = []
            for col in self.columns:
                value = item.get(col, '')
                # Format based on type
                if self.column_types.get(col) == 'number' and value != '':
                    try:
                        # Format numbers with commas
                        if isinstance(value, (int, float)):
                            value = f"{value:,}"
                    except:
                        pass
                values.append(str(value))
            
            self.data_tree.insert('', 'end', values=values)
        
        # Calculate unique values
        self.calculate_unique_values()
    
    def calculate_unique_values(self):
        """Calculate unique values for each column from filtered data"""
        self.column_unique_values = {}
        
        for col in self.columns:
            unique_vals = set()
            for item in self.filtered_data:
                val = item.get(col, '')
                if val != '':
                    unique_vals.add(str(val))
            self.column_unique_values[col] = sorted(list(unique_vals))
    
    def show_filter_menu(self, column):
        """Show filter menu for a specific column"""
        available_values = self.get_available_values_for_column(column)
        # Create filter dialog - need to find a suitable parent window
        parent_window = self.winfo_toplevel()
        FilterMenuDialog(parent_window, column, self.column_headers.get(column, column),
                        available_values, 
                        self.active_filters.get(column, set()), 
                        self.apply_filter)
    
    def get_available_values_for_column(self, column):
        """Get all possible values for a column considering OTHER column filters"""
        available_values = set()
        
        temp_filters = self.active_filters.copy()
        if column in temp_filters:
            del temp_filters[column]
        
        for item in self.original_data:
            include_item = True
            
            for filter_col, filter_values in temp_filters.items():
                item_value = str(item.get(filter_col, ''))
                if item_value not in filter_values:
                    include_item = False
                    break
            
            if include_item:
                val = item.get(column, '')
                if val != '':
                    available_values.add(str(val))
        
        return sorted(list(available_values))
    
    def apply_filter(self, column, selected_values):
        """Apply filter to a specific column"""
        if selected_values:
            self.active_filters[column] = set(selected_values)
        else:
            if column in self.active_filters:
                del self.active_filters[column]
        
        self.filter_data()
        self.update_display()
        self.update_column_headers()
    
    def filter_data(self):
        """Apply all active filters to the data"""
        self.filtered_data = []
        
        for item in self.original_data:
            include_item = True
            
            for filter_col, filter_values in self.active_filters.items():
                item_value = str(item.get(filter_col, ''))
                if item_value not in filter_values:
                    include_item = False
                    break
            
            if include_item:
                self.filtered_data.append(item)
    
    def update_display(self):
        """Update the grid display with filtered data"""
        self.populate_grid()

    def update_column_headers(self):
        """Update column headers to show filter indicators"""
        for col in self.columns:
            header_text = self.column_headers.get(col, col)
            if col in self.active_filters:
                self.data_tree.heading(col, text=f"{header_text} ▼")
            else:
                self.data_tree.heading(col, text=header_text)
    
    def clear_all_filters(self):
        """Clear all active filters"""
        self.active_filters = {}
        self.filtered_data = self.original_data.copy()
        self.update_display()
        self.update_column_headers()
    
    def refresh_data(self, new_data):
        """Refresh the view with new data"""
        self.original_data = new_data.copy() if new_data else []
        self.filtered_data = self.original_data.copy()
        self.clear_all_filters()
        self.populate_grid()
    
    def get_selected_items(self):
        """Get currently selected items"""
        selection = self.data_tree.selection()
        selected_items = []
        for item_id in selection:
            item_index = self.data_tree.index(item_id)
            if 0 <= item_index < len(self.filtered_data):
                selected_items.append(self.filtered_data[item_index])
        return selected_items
    
    def get_filtered_data(self):
        """Get the currently filtered data"""
        return self.filtered_data.copy()


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

