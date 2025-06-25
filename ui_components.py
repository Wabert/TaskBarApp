# ui_components.py
"""
Shared UI components for SuiteView Taskbar Application
Contains reusable dialogs, custom widgets, and styling functions
"""

import tkinter as tk
from tkinter import ttk
from config import Colors, Fonts, Dimensions
from utils import UIUtils

class CustomDialog(tk.Toplevel):
    """Base class for custom dialogs with consistent styling"""
    
    def __init__(self, parent, title, width=400, height=300, resizable=False):
        super().__init__(parent)
        self.parent = parent
        self.result = None
        
        # Initialize drag variables
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Initialize topmost maintenance
        self.maintain_topmost_active = True
        
        # Window setup
        self.configure(bg=Colors.DARK_GREEN)
        self.resizable(resizable, resizable)
        self.overrideredirect(True)  # Remove default title bar
        
        # Make dialog modal and always on top
        self.transient(parent)
        self.attributes('-topmost', True)
        self.lift()
        
        # Center on screen
        UIUtils.center_window(self, width, height)
        
        # Main content frame
        self.content_frame = tk.Frame(self, bg=Colors.LIGHT_GREEN, relief=tk.RAISED, bd=2)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Create custom title bar
        self.create_title_bar(title)
        
        # Container for dialog content
        self.dialog_content = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        self.dialog_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Button frame at bottom
        self.button_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN, height=50)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        self.button_frame.pack_propagate(False)
        
        # Make modal and ensure it stays on top
        self.grab_set()
        self.focus_force()
        
        # Schedule periodic topmost updates to ensure dialog stays visible
        self.after(100, self._maintain_topmost)
        
        # Pause parent's topmost maintenance if it exists
        if hasattr(parent, 'pause_topmost_maintenance'):
            parent.pause_topmost_maintenance()
        
        # Resume parent's topmost when this dialog is destroyed
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def create_title_bar(self, title):
        """Create custom title bar with drag functionality"""
        self.title_frame = tk.Frame(self.content_frame, bg=Colors.DARK_GREEN, height=25)
        self.title_frame.pack(fill=tk.X)
        self.title_frame.pack_propagate(False)
        
        # Drag handle (left side)
        drag_handle = tk.Label(self.title_frame, text="⋮⋮⋮", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                             font=('Arial', 8), cursor='fleur')
        drag_handle.pack(side=tk.LEFT, padx=3, pady=3)
        
        # Title label
        title_label = tk.Label(self.title_frame, text=f"📋 {title}", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                              font=Fonts.DIALOG_TITLE, cursor='fleur')
        title_label.pack(side=tk.LEFT, padx=5, pady=3)
        
        # Close button
        close_btn = tk.Label(self.title_frame, text="×", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                           font=('Arial', 12, 'bold'), cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=5)
        close_btn.bind("<Button-1>", lambda e: self.cancel())
        
        # Bind drag events to title bar elements
        for widget in [self.title_frame, drag_handle, title_label]:
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.do_drag)
            widget.bind("<ButtonRelease-1>", self.end_drag)
            widget.bind("<Enter>", lambda e: self.configure(cursor='fleur'))
            widget.bind("<Leave>", lambda e: self.configure(cursor=''))
        
        return self.title_frame
    
    def add_button(self, text, command, style='primary'):
        """Add a button to the button frame"""
        if style == 'primary':
            bg_color = Colors.DARK_GREEN
        elif style == 'secondary':
            bg_color = Colors.MEDIUM_GREEN
        else:
            bg_color = Colors.INACTIVE_GRAY
        
        button_container = tk.Frame(self.button_frame, bg=Colors.LIGHT_GREEN)
        button_container.pack(expand=True)
        
        btn = tk.Button(button_container, text=text, bg=bg_color, fg=Colors.WHITE,
                       command=command, width=Dimensions.DIALOG_BUTTON_WIDTH, 
                       font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        btn.pack(side=tk.LEFT, padx=5)
        
        return btn
    
    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.destroy()
    
    def ok(self):
        """OK button handler - override in subclasses"""
        self.result = True
        self.destroy()
    
    def start_drag(self, event):
        """Start dragging the dialog"""
        self.is_dragging = True
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        
        # Visual feedback
        self.title_frame.configure(bg=Colors.HOVER_GREEN)
        self.configure(cursor='fleur')
    
    def do_drag(self, event):
        """Handle drag motion"""
        if not self.is_dragging:
            return
        
        # Calculate the distance moved
        delta_x = event.x_root - self.drag_start_x
        delta_y = event.y_root - self.drag_start_y
        
        # Get current position
        current_x = self.winfo_x()
        current_y = self.winfo_y()
        
        # Calculate new position
        new_x = current_x + delta_x
        new_y = current_y + delta_y
        
        # Keep dialog on screen (basic bounds checking)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        # Ensure dialog stays on screen
        new_x = max(0, min(new_x, screen_width - dialog_width))
        new_y = max(0, min(new_y, screen_height - dialog_height))
        
        # Move the dialog
        self.geometry(f"+{new_x}+{new_y}")
        
        # Update start position for next move
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
    
    def end_drag(self, event):
        """End dragging operation"""
        self.is_dragging = False
        self.configure(cursor='')
        
        # Remove visual feedback
        self.title_frame.configure(bg=Colors.DARK_GREEN)
    
    def pause_topmost_maintenance(self):
        """Pause the topmost maintenance for this dialog"""
        self.maintain_topmost_active = False
    
    def resume_topmost_maintenance(self):
        """Resume the topmost maintenance for this dialog"""
        self.maintain_topmost_active = True
    
    def _maintain_topmost(self):
        """Periodically ensure dialog stays on top"""
        try:
            if self.winfo_exists() and self.maintain_topmost_active:
                # Only maintain topmost if no combobox is active to avoid stealing focus
                focused_widget = self.focus_get()
                if not (focused_widget and isinstance(focused_widget, ttk.Combobox)):
                    # Check if any combobox in the dialog has focus or is showing dropdown
                    combobox_active = self._has_active_combobox()
                    if not combobox_active:
                        self.lift()
                        self.attributes('-topmost', True)
                self.after(500, self._maintain_topmost)  # Check every 500ms
            elif self.winfo_exists():
                # Still schedule next check even if paused
                self.after(500, self._maintain_topmost)
        except:
            pass  # Dialog has been destroyed
    
    def _has_active_combobox(self):
        """Check if any combobox in the dialog is currently active (dropdown showing)"""
        try:
            # Recursively check all widgets to find active comboboxes
            return self._check_widget_for_active_combobox(self)
        except:
            return False
    
    def _check_widget_for_active_combobox(self, widget):
        """Recursively check widget and its children for active comboboxes"""
        try:
            # Check if current widget is an active combobox
            if isinstance(widget, ttk.Combobox):
                # Check if combobox has focus or its dropdown is showing
                if widget.focus_get() == widget:
                    return True
                # Additional check: see if the combobox state indicates dropdown is open
                try:
                    if 'pressed' in str(widget.state()) or 'active' in str(widget.state()):
                        return True
                except:
                    pass
            
            # Check all child widgets
            for child in widget.winfo_children():
                if self._check_widget_for_active_combobox(child):
                    return True
            
            return False
        except:
            return False
    
    def _on_closing(self):
        """Handle dialog closing"""
        # Resume parent's topmost maintenance
        if hasattr(self.parent, 'resume_topmost_maintenance'):
            self.parent.resume_topmost_maintenance()
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

# Updated FormField class (add this to ui_components.py)

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
            
            self.widget.pack(fill=tk.X, expand=True)
            
        else:
            # Original side-by-side layout
            self.label = tk.Label(self.frame, text=label_text, bg=Colors.LIGHT_GREEN, 
                                fg=Colors.BLACK, font=Fonts.DIALOG_LABEL)
            self.label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
            if field_type == 'entry':
                self.widget = tk.Entry(self.frame, font=Fonts.DIALOG_LABEL, **kwargs)
                self._bind_clipboard_operations()
            elif field_type == 'combobox':
                self.widget = ttk.Combobox(self.frame, font=Fonts.DIALOG_LABEL, **kwargs)
                self._bind_combobox_clipboard_operations()
            elif field_type == 'text':
                self.widget = tk.Text(self.frame, font=Fonts.DIALOG_LABEL, **kwargs)
                self._bind_text_clipboard_operations()
            
            self.widget.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
            self.frame.grid_columnconfigure(1, weight=1)
    
    def _bind_clipboard_operations(self):
        """Bind standard clipboard operations to Entry widget"""
        # Standard Windows/cross-platform shortcuts
        self.widget.bind('<Control-c>', self._copy)
        self.widget.bind('<Control-x>', self._cut)
        self.widget.bind('<Control-v>', self._paste)
        self.widget.bind('<Control-a>', self._select_all)
        
        # Right-click context menu
        self.widget.bind('<Button-3>', self._show_context_menu)
    
    def _bind_combobox_clipboard_operations(self):
        """Bind clipboard operations to Combobox widget"""
        # Comboboxes need special handling since they have different methods
        self.widget.bind('<Control-c>', self._copy_combobox)
        self.widget.bind('<Control-x>', self._cut_combobox)
        self.widget.bind('<Control-v>', self._paste_combobox)
        self.widget.bind('<Control-a>', self._select_all_combobox)
        
        # Right-click context menu
        self.widget.bind('<Button-3>', self._show_combobox_context_menu)
    
    def _bind_text_clipboard_operations(self):
        """Enhance Text widget clipboard operations"""
        # Text widgets already have built-in clipboard support, but we can add context menu
        self.widget.bind('<Button-3>', self._show_text_context_menu)
    
    def _copy(self, event=None):
        """Copy selected text to clipboard"""
        try:
            if self.widget.selection_present():
                self.widget.clipboard_clear()
                self.widget.clipboard_append(self.widget.selection_get())
        except tk.TclError:
            pass  # No selection
        return 'break'
    
    def _cut(self, event=None):
        """Cut selected text to clipboard"""
        try:
            if self.widget.selection_present():
                self.widget.clipboard_clear()
                self.widget.clipboard_append(self.widget.selection_get())
                self.widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass  # No selection
        return 'break'
    
    def _paste(self, event=None):
        """Paste from clipboard"""
        try:
            clipboard_text = self.widget.clipboard_get()
            if self.widget.selection_present():
                self.widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.widget.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            pass  # No clipboard content
        return 'break'
    
    def _select_all(self, event=None):
        """Select all text"""
        self.widget.select_range(0, tk.END)
        self.widget.icursor(tk.END)
        return 'break'
    
    def _copy_combobox(self, event=None):
        """Copy from combobox"""
        try:
            if self.widget.selection_present():
                self.widget.clipboard_clear()
                self.widget.clipboard_append(self.widget.selection_get())
        except (tk.TclError, AttributeError):
            # Fallback: copy entire value if no selection
            try:
                self.widget.clipboard_clear()
                self.widget.clipboard_append(self.widget.get())
            except:
                pass
        return 'break'
    
    def _cut_combobox(self, event=None):
        """Cut from combobox"""
        try:
            if self.widget.selection_present():
                self.widget.clipboard_clear()
                self.widget.clipboard_append(self.widget.selection_get())
                # For combobox, we can delete selected text
                start = self.widget.index(tk.SEL_FIRST)
                end = self.widget.index(tk.SEL_LAST)
                current_value = self.widget.get()
                new_value = current_value[:start] + current_value[end:]
                self.widget.set(new_value)
        except (tk.TclError, AttributeError):
            pass
        return 'break'
    
    def _paste_combobox(self, event=None):
        """Paste to combobox"""
        try:
            clipboard_text = self.widget.clipboard_get()
            if self.widget.selection_present():
                # Replace selection
                start = self.widget.index(tk.SEL_FIRST)
                end = self.widget.index(tk.SEL_LAST)
                current_value = self.widget.get()
                new_value = current_value[:start] + clipboard_text + current_value[end:]
                self.widget.set(new_value)
            else:
                # Insert at cursor position
                cursor_pos = self.widget.index(tk.INSERT)
                current_value = self.widget.get()
                new_value = current_value[:cursor_pos] + clipboard_text + current_value[cursor_pos:]
                self.widget.set(new_value)
        except tk.TclError:
            pass
        return 'break'
    
    def _select_all_combobox(self, event=None):
        """Select all text in combobox"""
        try:
            self.widget.selection_range(0, tk.END)
            self.widget.icursor(tk.END)
        except (tk.TclError, AttributeError):
            pass
        return 'break'
    
    def _show_context_menu(self, event):
        """Show right-click context menu for Entry"""
        context_menu = tk.Menu(self.widget, tearoff=0)
        
        # Check if there's a selection
        has_selection = False
        try:
            has_selection = self.widget.selection_present()
        except:
            pass
        
        # Check if clipboard has content
        has_clipboard = False
        try:
            self.widget.clipboard_get()
            has_clipboard = True
        except:
            pass
        
        context_menu.add_command(label="Cut", command=self._cut, 
                               state=tk.NORMAL if has_selection else tk.DISABLED)
        context_menu.add_command(label="Copy", command=self._copy,
                               state=tk.NORMAL if has_selection else tk.DISABLED)
        context_menu.add_command(label="Paste", command=self._paste,
                               state=tk.NORMAL if has_clipboard else tk.DISABLED)
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=self._select_all)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _show_combobox_context_menu(self, event):
        """Show right-click context menu for Combobox"""
        context_menu = tk.Menu(self.widget, tearoff=0)
        
        # Check if there's a selection
        has_selection = False
        try:
            has_selection = self.widget.selection_present()
        except:
            pass
        
        # Check if clipboard has content
        has_clipboard = False
        try:
            self.widget.clipboard_get()
            has_clipboard = True
        except:
            pass
        
        context_menu.add_command(label="Cut", command=self._cut_combobox,
                               state=tk.NORMAL if has_selection else tk.DISABLED)
        context_menu.add_command(label="Copy", command=self._copy_combobox,
                               state=tk.NORMAL if (has_selection or self.widget.get()) else tk.DISABLED)
        context_menu.add_command(label="Paste", command=self._paste_combobox,
                               state=tk.NORMAL if has_clipboard else tk.DISABLED)
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=self._select_all_combobox,
                               state=tk.NORMAL if self.widget.get() else tk.DISABLED)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _show_text_context_menu(self, event):
        """Show right-click context menu for Text widget"""
        # Text widgets have built-in context menus in some systems,
        # but we can provide a custom one for consistency
        context_menu = tk.Menu(self.widget, tearoff=0)
        
        # Check if there's a selection
        has_selection = False
        try:
            has_selection = bool(self.widget.tag_ranges(tk.SEL))
        except:
            pass
        
        # Check if clipboard has content
        has_clipboard = False
        try:
            self.widget.clipboard_get()
            has_clipboard = True
        except:
            pass
        
        context_menu.add_command(label="Cut", command=lambda: self.widget.event_generate("<<Cut>>"),
                               state=tk.NORMAL if has_selection else tk.DISABLED)
        context_menu.add_command(label="Copy", command=lambda: self.widget.event_generate("<<Copy>>"),
                               state=tk.NORMAL if has_selection else tk.DISABLED)
        context_menu.add_command(label="Paste", command=lambda: self.widget.event_generate("<<Paste>>"),
                               state=tk.NORMAL if has_clipboard else tk.DISABLED)
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=lambda: self.widget.tag_add(tk.SEL, "1.0", tk.END))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        return self
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        return self
    
    def get(self):
        if hasattr(self.widget, 'get'):
            return self.widget.get()
        return ""
    
    def set(self, value):
        if hasattr(self.widget, 'delete') and hasattr(self.widget, 'insert'):
            self.widget.delete(0, tk.END)
            self.widget.insert(0, value)
        elif hasattr(self.widget, 'set'):
            self.widget.set(value)

class StyledButton(tk.Button):
    """Custom styled button"""
    
    def __init__(self, parent, text, style='primary', **kwargs):
        # Set default styling based on style type
        if style == 'primary':
            bg_color = Colors.DARK_GREEN
            fg_color = Colors.WHITE
        elif style == 'secondary':
            bg_color = Colors.MEDIUM_GREEN
            fg_color = Colors.BLACK
        elif style == 'success':
            bg_color = Colors.LIGHT_GREEN
            fg_color = Colors.BLACK
        else:  # 'danger' or other
            bg_color = Colors.INACTIVE_GRAY
            fg_color = Colors.WHITE
        
        defaults = {
            'bg': bg_color,
            'fg': fg_color,
            'font': Fonts.DIALOG_BUTTON,
            'relief': tk.RAISED,
            'bd': 1,
            'cursor': 'hand2',
            'activebackground': Colors.HOVER_GREEN,
            'activeforeground': Colors.WHITE
        }
        
        # Override defaults with provided kwargs
        defaults.update(kwargs)
        
        super().__init__(parent, text=text, **defaults)

class CategoryHeader(tk.Frame):
    """Styled category header for lists"""
    
    def __init__(self, parent, title, **kwargs):
        super().__init__(parent, bg=Colors.MEDIUM_GREEN, relief=tk.RAISED, bd=1, **kwargs)
        
        self.title_label = tk.Label(self, text=title, bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                                   font=Fonts.MENU_HEADER, height=1)
        self.title_label.pack(pady=1)
    
    def set_title(self, title):
        self.title_label.config(text=title)