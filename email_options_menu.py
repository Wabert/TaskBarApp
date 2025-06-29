# email_options_menu.py
"""
Email options popup menu for SuiteView Taskbar
Shows options for viewing received and sent attachments
"""

import tkinter as tk
from config import Colors, Fonts
from email_menu import EmailAttachmentsMenu

class EmailOptionsMenu(tk.Toplevel):
    """Popup menu for email options"""
    
    def __init__(self, parent, x, y, taskbar_instance):
        super().__init__(parent)
        self.parent = parent
        self.taskbar_instance = taskbar_instance
        
        # Window setup
        self.overrideredirect(True)
        self.configure(bg=Colors.DARK_GREEN)
        # NO TOPMOST - This makes everything simpler!
        # self.attributes('-topmost', True)  # REMOVED
        self.attributes('-alpha', 0.98)
        
        # Main container
        self.main_frame = tk.Frame(self, bg=Colors.DARK_GREEN, relief=tk.RAISED, bd=2)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create menu items
        self.create_menu_items()
        
        # Update to get proper dimensions
        self.update_idletasks()
        width = max(250, self.winfo_reqwidth())
        height = self.winfo_reqheight()
        
        # Position menu with bottom edge at top of taskbar
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Set up focus handling for click-outside behavior
        self.focus_set()
        
        # Bind focus loss to close the menu
        self.bind("<FocusOut>", self.on_focus_out)
        
        # Also bind to the root window to catch clicks anywhere
        self.bind_id = self.parent.bind("<Button-1>", self.on_root_click, "+")
        
        # Track if we're over the menu
        self.bind("<Enter>", lambda e: setattr(self, 'mouse_over_menu', True))
        self.bind("<Leave>", lambda e: setattr(self, 'mouse_over_menu', False))
        self.mouse_over_menu = False
    
    def on_root_click(self, event):
        """Handle clicks on the root window (outside menu)"""
        try:
            # Get the widget under the mouse
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
            
            # Check if the click is outside our menu
            if widget not in [self] + self.get_all_children(self):
                self.close_menu()
        except:
            # If any error occurs, it's safe to close
            self.close_menu()
    
    def get_all_children(self, widget):
        """Recursively get all children of a widget"""
        children = []
        for child in widget.winfo_children():
            children.append(child)
            children.extend(self.get_all_children(child))
        return children
    
    def on_focus_out(self, event):
        """Handle focus loss"""
        # Small delay to prevent premature closing when clicking menu items
        self.after(100, self.check_focus)
    
    def check_focus(self):
        """Check if focus has truly left the menu"""
        try:
            focused_widget = self.focus_get()
            if focused_widget not in [self] + self.get_all_children(self):
                self.close_menu()
        except:
            pass
    
    def close_menu(self):
        """Close the menu properly"""
        try:
            # Unbind the root click handler
            if hasattr(self, 'bind_id'):
                self.parent.unbind("<Button-1>", self.bind_id)
        except:
            pass
        
        self.destroy()
    
    def destroy(self):
        """Clean up and destroy"""
        try:
            # Make sure to unbind from parent
            if hasattr(self, 'bind_id'):
                self.parent.unbind("<Button-1>", self.bind_id)
        except:
            pass
        
        super().destroy()
    
    def create_menu_items(self):
        """Create the menu options"""
        # Header with larger icon
        header_frame = tk.Frame(self.main_frame, bg=Colors.DARK_GREEN)
        header_frame.pack(fill=tk.X, pady=5)
        
        # Larger icon for header
        header_icon = tk.Label(header_frame, text="📧", 
                             bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                             font=('Arial', 20))
        header_icon.pack(side=tk.LEFT, padx=(10, 5))
        
        header_text = tk.Label(header_frame, text="Email Options", 
                             bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                             font=Fonts.MENU_HEADER)
        header_text.pack(side=tk.LEFT)
        
        # Separator
        separator = tk.Frame(self.main_frame, height=1, bg=Colors.MEDIUM_GREEN)
        separator.pack(fill=tk.X, padx=5, pady=2)
        
        # Menu items container
        items_frame = tk.Frame(self.main_frame, bg=Colors.LIGHT_GREEN)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Attachments Received option with larger icon
        received_item = self.create_menu_item(
            items_frame, 
            "📥",
            "Attachments Received", 
            self.show_received_attachments
        )
        received_item.pack(fill=tk.X, padx=2, pady=1)
        
        # Attachments Sent option with larger icon
        sent_item = self.create_menu_item(
            items_frame, 
            "📤",
            "Attachments Sent", 
            self.show_sent_attachments
        )
        sent_item.pack(fill=tk.X, padx=2, pady=1)
    
    def create_menu_item(self, parent, icon, text, command):
        """Create a single menu item with separate icon and text"""
        item_frame = tk.Frame(parent, bg=Colors.LIGHT_GREEN)
        
        # Large icon on the left
        icon_label = tk.Label(item_frame, text=icon, bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                            font=('Arial', 18), width=2, anchor='center')
        icon_label.pack(side=tk.LEFT, padx=(10, 5))
        
        # Text label
        text_label = tk.Label(item_frame, text=text, bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                            font=Fonts.MENU_ITEM, anchor='w')
        text_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Hover effect for the entire frame
        def on_enter(e):
            item_frame.configure(bg=Colors.HOVER_GREEN)
            icon_label.configure(bg=Colors.HOVER_GREEN, fg=Colors.WHITE)
            text_label.configure(bg=Colors.HOVER_GREEN, fg=Colors.WHITE)
        
        def on_leave(e):
            item_frame.configure(bg=Colors.LIGHT_GREEN)
            icon_label.configure(bg=Colors.LIGHT_GREEN, fg=Colors.BLACK)
            text_label.configure(bg=Colors.LIGHT_GREEN, fg=Colors.BLACK)
        
        # Bind events to all components
        for widget in [item_frame, icon_label, text_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: self.execute_command(command))
            widget.configure(cursor='hand2')
        
        # Set minimum height for the frame
        item_frame.configure(height=35)
        item_frame.pack_propagate(False)
        
        return item_frame
    
    def execute_command(self, command):
        """Execute menu command and close menu"""
        self.close_menu()
        command()
    
    def show_received_attachments(self):
        """Show received email attachments"""
        # Get the taskbar instance
        taskbar = self.taskbar_instance
            
        if not hasattr(taskbar, 'email_menu'):
            from email_menu import EmailAttachmentsMenu
            taskbar.email_menu = EmailAttachmentsMenu(taskbar.root)
        
        # Show received attachments (default behavior)
        taskbar.email_menu.show_email_attachments(email_type='received')
    
    def show_sent_attachments(self):
        """Show sent email attachments"""
        # Get the taskbar instance
        taskbar = self.taskbar_instance
            
        if not hasattr(taskbar, 'email_menu'):
            from email_menu import EmailAttachmentsMenu
            taskbar.email_menu = EmailAttachmentsMenu(taskbar.root)
        
        # Show sent attachments
        taskbar.email_menu.show_email_attachments(email_type='sent')