# email_options_menu.py
"""
Email options popup menu for SuiteView Taskbar
Updated to use SimpleWindow from simple_window_factory
"""

import tkinter as tk
from simple_window_factory import SimpleWindow
from config import Colors, Fonts
from email_menu import EmailAttachmentsMenu

class EmailOptionsMenu(SimpleWindow):
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
        self.button = button
        
        # Initialize with no resize handles for menu
        super().__init__(parent, "Email Options", resize_handles=None)
        
        # Position near button
        self._position_near_button()
        
        # Set transparency
        self.attributes('-alpha', 0.98)
        
        # Track mouse over menu for hover effects
        self.bind("<Enter>", lambda e: setattr(self, 'mouse_over_menu', True))
        self.bind("<Leave>", lambda e: setattr(self, 'mouse_over_menu', False))
        self.mouse_over_menu = False
        
        # Create the menu content
        self._create_menu_content()
        
        # Enable click-outside detection
        self._setup_click_outside_detection()
    
    def _position_near_button(self):
        """Position menu near the button that triggered it"""
        if self.button:
            # Get button position
            button_x = self.button.winfo_rootx()
            button_y = self.button.winfo_rooty()
            button_height = self.button.winfo_height()
            
            # Position menu below button
            self.geometry(f"+{button_x}+{button_y + button_height + 5}")
    
    def _create_menu_content(self):
        """Create the menu content"""
        # Override the light green background with dark green for menu style
        self.content_frame.configure(bg=Colors.DARK_GREEN)
        
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
        item_frame = tk.Frame(parent, bg=Colors.LIGHT_GREEN, height=35)
        item_frame.pack_propagate(False)
        
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
        
        return item_frame
    
    def _setup_click_outside_detection(self):
        """Set up detection for clicks outside the menu"""
        # Bind to all windows to detect clicks anywhere
        self.bind_all("<Button-1>", self._check_click_outside, "+")
        
    def _check_click_outside(self, event):
        """Check if click was outside the menu"""
        try:
            # Get the widget that was clicked
            clicked_widget = event.widget
            
            # Check if the clicked widget is part of this menu
            widget = clicked_widget
            while widget:
                if widget == self:
                    # Click was inside the menu
                    return
                widget = widget.master
            
            # Click was outside - close the menu
            self.close_window()
        except:
            pass
    
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
    
    def close_window(self):
        """Override to clean up bindings before closing"""
        try:
            # Unbind the click detection
            self.unbind_all("<Button-1>")
        except:
            pass
        # Call parent close method
        super().close_window()