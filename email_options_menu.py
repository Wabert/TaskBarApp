# email_options_menu.py
"""
Email options popup menu for SuiteView Taskbar
Shows options for viewing received and sent attachments
Simplified version using base class click-outside detection
"""

import tkinter as tk
from window_factory import BaseWindow
from config import Colors, Fonts
from email_menu import EmailAttachmentsMenu

class EmailOptionsMenu(BaseWindow):
    """Popup menu for email options"""

    def __init__(self, parent, button, taskbar_instance):
        """
        Initialize email options menu
        
        Args:
            parent: Parent window
            button: The button that triggered this menu
            taskbar_instance: Reference to the main taskbar
        """
        self.taskbar_instance = taskbar_instance
        
        # Initialize with taskbar_menu type and pass button for positioning
        super().__init__(parent, "", "taskbar_menu", button=button)
        
        # Set transparency
        self.attributes('-alpha', 0.98)
        
        # Track mouse over menu for hover effects
        self.bind("<Enter>", lambda e: setattr(self, 'mouse_over_menu', True))
        self.bind("<Leave>", lambda e: setattr(self, 'mouse_over_menu', False))
        self.mouse_over_menu = False
    
    def create_content(self):
        """Create the menu content"""
        # Override background color for the menu
        self.content_frame.configure(bg=Colors.DARK_GREEN)
        
        # Header with larger icon
        header_frame = tk.Frame(self.content_frame, bg=Colors.DARK_GREEN)
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
        separator = tk.Frame(self.content_frame, height=1, bg=Colors.MEDIUM_GREEN)
        separator.pack(fill=tk.X, padx=5, pady=2)
        
        # Menu items container with light background
        items_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Attachments Received option
        received_item = self._create_menu_item(
            items_frame, 
            "📥",
            "Attachments Received", 
            self.show_received_attachments
        )
        received_item.pack(fill=tk.X, padx=2, pady=1)
        
        # Attachments Sent option
        sent_item = self._create_menu_item(
            items_frame, 
            "📤",
            "Attachments Sent", 
            self.show_sent_attachments
        )
        sent_item.pack(fill=tk.X, padx=2, pady=1)
        
        # Update window size after content is created
        self.update_idletasks()
        width = max(250, self.winfo_reqwidth())
        self.geometry(f"{width}x{self.winfo_reqheight()}")
    
    def _create_menu_item(self, parent, icon, text, command):
        """Create a single menu item with icon and text"""
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
            widget.bind("<Button-1>", lambda e: self._execute_command(command))
            widget.configure(cursor='hand2')
        
        # Set minimum height for the frame
        item_frame.configure(height=35)
        item_frame.pack_propagate(False)
        
        return item_frame
    
    def _execute_command(self, command):
        """Execute menu command and close menu"""
        # Close menu first
        self.close_window()
        # Then execute command
        command()
    
    def show_received_attachments(self):
        """Show received email attachments"""
        # Get the taskbar instance
        taskbar = self.taskbar_instance
            
        if not hasattr(taskbar, 'email_menu'):
            taskbar.email_menu = EmailAttachmentsMenu(taskbar.root)
        
        # Show received attachments (default behavior)
        taskbar.email_menu.show_email_attachments(email_type='received')
    
    def show_sent_attachments(self):
        """Show sent email attachments"""
        # Get the taskbar instance
        taskbar = self.taskbar_instance
            
        if not hasattr(taskbar, 'email_menu'):
            taskbar.email_menu = EmailAttachmentsMenu(taskbar.root)
        
        # Show sent attachments
        taskbar.email_menu.show_email_attachments(email_type='sent')
    
    def _create_window_structure(self):
        """Override to create custom structure for menu"""
        # Don't create the standard titlebar for menus
        # Just create the content frame with dark background
        self.content_frame = tk.Frame(self, bg=Colors.DARK_GREEN, relief=tk.RAISED, bd=2)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    def on_closing(self):
        """Cleanup when closing"""
        # Any cleanup code if needed
        pass