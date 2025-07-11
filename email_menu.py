# email_menu.py
"""
Updated email attachments menu with support for both received and sent emails
"""

import tkinter as tk
from simple_window_factory import InventoryViewWindow
from email_manager import EmailManager
from ui_components import CustomDialog, WarningDialog
from config import Colors, Fonts, Dimensions
import threading

class EmailAttachmentsMenu:
    """Enhanced email attachments menu with caching and support for sent/received"""
    
    def __init__(self, parent_window):
        """Initialize the email attachments menu"""
        self.parent = parent_window
        self.email_manager = EmailManager(weeks_back=8)
        self.inventory_window = None
        self.loading_dialog = None
    
    def show_email_attachments(self, force_refresh: bool = False, email_type: str = 'received'):
        """
        Display the email attachments in an inventory view window
        
        Args:
            force_refresh: Force a fresh scan
            email_type: 'received' or 'sent'
        """
        # Check if we need to do a fresh scan
        scan_type = EmailManager.SCAN_ATTACHMENTS if email_type == 'received' else EmailManager.SCAN_ATTACHMENTS_SENT
        cache_exists = self.email_manager.get_cache_info(scan_type) is not None
        needs_fresh_scan = force_refresh or not cache_exists or not self.email_manager.cache.is_cache_valid(scan_type)
        
        if needs_fresh_scan:
            # Show loading indicator and scan in background
            self.show_loading_dialog(email_type)
            
            scan_thread = threading.Thread(
                target=self._perform_scan,
                args=(email_type,),
                daemon=True
            )
            scan_thread.start()
        else:
            # Use cached data directly
            result = self.email_manager.get_emails_with_attachments(
                use_cache=True, 
                force_refresh=False,
                email_type=email_type
            )
            self._display_emails_from_result(result, email_type)
    
    def _perform_scan(self, email_type: str):
        """Perform email scan in background thread"""
        result = self.email_manager.get_emails_with_attachments(
            use_cache=False,
            force_refresh=True,
            email_type=email_type
        )
        
        if self.loading_dialog:
            self.loading_dialog.after(0, lambda: self._scan_complete(result, email_type))
    
    def _scan_complete(self, result: dict, email_type: str):
        """Handle scan completion"""
        # Close loading dialog
        if self.loading_dialog:
            self.loading_dialog.destroy()
            self.loading_dialog = None
        
        # Display results
        self._display_emails_from_result(result, email_type)
    
    def _display_emails_from_result(self, result: dict, email_type: str):
        """Display emails from scan result"""
        attachments = result['data']
        metadata = result.get('metadata', {})
        from_cache = result.get('from_cache', False)
        
        # Prepare window configuration
        window_config = {
            'title': f"Email Attachments - {email_type.capitalize()}",
            'window_width': 1200,
            'window_height': 600,
            'columns': [
                {'key': 'Subject', 'header': 'Subject', 'width': 300},
                {'key': 'AttachmentName', 'header': 'Attachment', 'width': 250},
                {'key': 'Extension', 'header': 'Type', 'width': 80},
                {'key': 'ReceivedTime', 'header': 'Date', 'width': 150}
            ],
            'additional_info': self._get_additional_info(metadata, from_cache, email_type)
        }
        
        # Format the attachment data for display
        display_data = []
        for att in attachments:
            display_data.append({
                'Subject': att.get('Subject', ''),
                'AttachmentName': att.get('AttachmentName', ''),
                'Extension': att.get('Extension', 'Unknown'),
                'ReceivedTime': att.get('ReceivedTime', '')[:10],  # Just date part
                'EntryID': att.get('EntryID', ''),
                'AttachmentIndex': att.get('AttachmentIndex', 0)
            })
        
        # Create new inventory window using EmailInventoryWindow class
        if self.inventory_window:
            self.inventory_window.destroy()
        
        self.inventory_window = EmailInventoryWindow(
            self.parent,
            display_data,
            window_config,
            quick_refresh_callback=lambda: self._quick_refresh(email_type),
            full_refresh_callback=lambda: self.show_email_attachments(force_refresh=True, email_type=email_type),
            email_type=email_type
        )

    def _quick_refresh(self, email_type: str):
        """Quick refresh using cached data"""
        result = self.email_manager.get_emails_with_attachments(
            use_cache=True,
            force_refresh=False,
            email_type=email_type
        )
        if self.inventory_window and hasattr(self.inventory_window, 'update_with_new_data'):
            # Format the data
            display_data = []
            for att in result['data']:
                display_data.append({
                    'Subject': att.get('Subject', ''),
                    'AttachmentName': att.get('AttachmentName', ''),
                    'Extension': att.get('Extension', 'Unknown'),
                    'ReceivedTime': att.get('ReceivedTime', '')[:10],
                    'EntryID': att.get('EntryID', ''),
                    'AttachmentIndex': att.get('AttachmentIndex', 0)
                })
            self.inventory_window.update_with_new_data(display_data)
            
            # Update additional info
            metadata = result.get('metadata', {})
            from_cache = result.get('from_cache', False)
            if hasattr(self.inventory_window, 'refresh_status_label'):
                status_text = self._get_status_text(metadata, from_cache, email_type)
                self.inventory_window.refresh_status_label.config(text=status_text)

    def _get_additional_info(self, metadata: dict, from_cache: bool, email_type: str) -> dict:
        """Get additional info for the window header"""
        info = {}
        
        if metadata:
            if 'total_attachment_lines' in metadata:
                info['Attachments'] = f"{metadata['total_attachment_lines']:,}"
            if 'total_emails_with_attachments' in metadata:
                info['Emails'] = f"{metadata['total_emails_with_attachments']:,}"
            if 'weeks_back' in metadata:
                info['Period'] = f"{metadata['weeks_back']} weeks"
        
        info['Source'] = 'Cached' if from_cache else 'Fresh Scan'
        
        return info
    
    def _handle_item_click(self, item: dict, column_key: str = None):
        """Handle clicks on specific columns"""
        if not column_key:
            return
            
        if column_key == 'Subject':
            # Open the email
            self._open_email(item)
        elif column_key == 'AttachmentName':
            # Open the attachment
            self._open_attachment(item)
    
    def _open_attachment(self, attachment_data: dict):
        """Handle click on attachment to open it"""
        if 'EntryID' in attachment_data and 'AttachmentIndex' in attachment_data:
            self.email_manager.open_attachment(
                attachment_data['EntryID'], 
                attachment_data['AttachmentIndex']
            )

    def refresh_emails(self, email_type: str):
        """Quick refresh - check for new emails only"""
        if self.inventory_window and hasattr(self.inventory_window, 'show_refreshing'):
            self.inventory_window.show_refreshing()
        
        # For now, just do a full refresh
        # Could be optimized later to only check recent emails
        thread = threading.Thread(
            target=self._perform_quick_refresh,
            args=(email_type,),
            daemon=True
        )
        thread.start()
    
    def _perform_quick_refresh(self, email_type: str):
        """Perform quick refresh in background"""
        result = self.email_manager.get_emails_with_attachments(
            use_cache=False,
            force_refresh=True,
            email_type=email_type
        )
        
        if self.inventory_window:
            self.inventory_window.after(0, lambda: self._update_inventory(result))
    
    def full_refresh_emails(self, email_type: str):
        """Full refresh - rescan all emails"""
        if self.inventory_window:
            self.inventory_window.destroy()
        self.show_email_attachments(force_refresh=True, email_type=email_type)
    
    def _update_inventory(self, result: dict):
        """Update inventory window with new data"""
        if self.inventory_window and self.inventory_window.winfo_exists():
            # Update the data
            self.inventory_window.original_data = result['data']
            self.inventory_window.filtered_data = result['data']
            self.inventory_window.populate_grid()
            self.inventory_window.update_stats()
            
            # Show refresh complete message
            self.inventory_window.show_refresh_complete("Refresh complete")
    
    def _open_email(self, email_data: dict):
        """Handle double-click on email item to open it"""
        if 'EntryID' in email_data:
            self.email_manager.open_email(email_data['EntryID'])
    
    def _show_no_emails_message(self, email_type: str):
        """Show a message when no emails with attachments are found"""
        email_type_text = "sent" if email_type == 'sent' else "received"
        WarningDialog.show(
            self.parent,
            "No Emails Found",
            f"No {email_type_text} emails with attachments found in the last {self.email_manager.weeks_back} weeks."
        )
    
    def show_loading_dialog(self, email_type: str):
        """Show loading dialog during email scan"""
        email_type_text = "sent" if email_type == 'sent' else "received"
        self.loading_dialog = LoadingDialog(self.parent, f"Scanning {email_type_text} emails...")


class EmailInventoryWindow(InventoryViewWindow):
    """Email attachments window using the new InventoryViewWindow"""
    
    def __init__(self, parent, data, config, quick_refresh_callback, full_refresh_callback, email_type):
        self.quick_refresh_callback = quick_refresh_callback
        self.full_refresh_callback = full_refresh_callback
        self.email_type = email_type
        
        # Add double-click handler to open attachments
        config['on_item_double_click'] = self._open_attachment
        
        # Initialize parent InventoryViewWindow
        super().__init__(parent, data, config)
        
        # Add custom refresh buttons to footer
        self._add_refresh_buttons()
    
    def _add_refresh_buttons(self):
        """Add email-specific refresh buttons to the footer"""
        # Find the footer frame (it's the dark green frame at bottom)
        for child in self.content_frame.winfo_children():
            if isinstance(child, tk.Frame) and child.cget('bg') == Colors.DARK_GREEN:
                footer_frame = child
                break
        else:
            return
        
        # Find the button frame (right side of footer)
        for child in footer_frame.winfo_children():
            if isinstance(child, tk.Frame) and child.pack_info().get('side') == 'right':
                button_frame = child
                break
        else:
            return
        
        # Add separator
        separator = tk.Frame(button_frame, bg=Colors.WHITE, width=2)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Quick refresh button (uses cache)
        quick_refresh_btn = tk.Button(button_frame, text="Quick Refresh", 
                                     bg=Colors.MEDIUM_GREEN, fg=Colors.WHITE,
                                     relief=tk.RAISED, bd=1, cursor='hand2',
                                     font=Fonts.MENU_ITEM, padx=10,
                                     command=self.quick_refresh_callback)
        quick_refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Full refresh button (fresh scan)
        full_refresh_btn = tk.Button(button_frame, text="Full Refresh", 
                                    bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                                    relief=tk.RAISED, bd=1, cursor='hand2',
                                    font=Fonts.MENU_ITEM, padx=10,
                                    command=self.full_refresh_callback)
        full_refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Add refresh status label
        self.refresh_status_label = tk.Label(footer_frame, text="", 
                                           bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                                           font=Fonts.MENU_ITEM)
        self.refresh_status_label.pack(side=tk.LEFT, padx=10)
    
    def _open_attachment(self, item):
        """Open the selected attachment"""
        if 'EntryID' in item and 'AttachmentIndex' in item:
            try:
                # Use the email manager to open attachment
                from email_manager import EmailManager
                email_manager = EmailManager()
                email_manager.open_attachment(item['EntryID'], item['AttachmentIndex'])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open attachment: {str(e)}")
    
    def update_with_new_data(self, data):
        """Update the window with new data (for refresh)"""
        self.original_data = data.copy() if data else []
        self.filtered_data = self.original_data.copy()
        self.active_filters = {}  # Clear filters on refresh
        self.update_display()
        self.update_filter_status()
        self.update_column_headers()


class LoadingDialog(CustomDialog):
    """Simple loading dialog"""
    
    def __init__(self, parent, message="Loading..."):
        super().__init__(parent, "Please Wait", width=300, height=150)
        
        # Loading message
        msg_label = tk.Label(self.dialog_content, text=message,
                           bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                           font=Fonts.DIALOG_LABEL)
        msg_label.pack(pady=20)
        
        # Progress indicator (simple animation)
        self.progress_label = tk.Label(self.dialog_content, text="⏳",
                                     bg=Colors.LIGHT_GREEN, fg=Colors.DARK_GREEN,
                                     font=('Arial', 24))
        self.progress_label.pack(pady=10)
        
        # Remove button frame
        self.button_frame.pack_forget()
        
        # Start animation
        self.animate_progress()
    
    def animate_progress(self):
        """Simple progress animation"""
        current = self.progress_label.cget("text")
        if current == "⏳":
            self.progress_label.config(text="⌛")
        else:
            self.progress_label.config(text="⏳")
        
        self.after(500, self.animate_progress)