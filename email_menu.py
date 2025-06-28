# email_menu.py
"""
Enhanced email attachments menu with caching and refresh capabilities
"""

import tkinter as tk
from inventory_view_window import InventoryViewWindow
from email_manager import EmailManager
from ui_components import CustomDialog, WarningDialog
from config import Colors, Fonts, Dimensions
import threading

class EmailAttachmentsMenu:
    """Enhanced email attachments menu with caching"""
    
    def __init__(self, parent_window):
        """Initialize the email attachments menu"""
        self.parent = parent_window
        self.email_manager = EmailManager(weeks_back=8)
        self.inventory_window = None
        self.loading_dialog = None
    
    def show_email_attachments(self, force_refresh: bool = False):
        """Display the email attachments in an inventory view window"""
        # Check if we need to do a fresh scan
        cache_exists = self.email_manager.get_cache_info(EmailManager.SCAN_ATTACHMENTS) is not None
        needs_fresh_scan = force_refresh or not cache_exists or not self.email_manager.cache.is_cache_valid(EmailManager.SCAN_ATTACHMENTS)
        
        if needs_fresh_scan:
            # Show loading indicator and scan in background
            self.show_loading_dialog()
            
            scan_thread = threading.Thread(
                target=self._perform_scan,
                args=(),  # No args needed
                daemon=True
            )
            scan_thread.start()
        else:
            # Use cached data directly
            result = self.email_manager.get_emails_with_attachments(use_cache=True, force_refresh=False)
            self._display_emails_from_result(result)
    
    def _perform_scan(self):
        """Perform email scan in background thread - always fresh"""
        result = self.email_manager.get_emails_with_attachments(
            use_cache=False,
            force_refresh=True
        )
        
        if self.loading_dialog:
            self.loading_dialog.after(0, lambda: self._scan_complete(result))
    
    def _scan_complete(self, result: dict):
        """Handle scan completion"""
        # Close loading dialog
        if self.loading_dialog:
            self.loading_dialog.destroy()
            self.loading_dialog = None
        
        # Display results
        self._display_emails_from_result(result)
    
    def _display_emails(self, force_refresh: bool = False):
        """Display emails (from cache or fresh scan)"""
        result = self.email_manager.get_emails_with_attachments(
            use_cache=not force_refresh,
            force_refresh=force_refresh
        )
        self._display_emails_from_result(result)
    
    def _display_emails_from_result(self, result: dict):
        """Display emails from scan result"""
        attachments = result['data']
        metadata = result.get('metadata', {})
        from_cache = result.get('from_cache', False)
        
        if not attachments:
            self._show_no_emails_message()
            return
        
        # Prepare additional info
        additional_info = {
            'Period': f"Last {metadata.get('weeks_back', 2)} weeks",
            'Total Emails': metadata.get('total_emails_with_attachments', 'Unknown'),
            'Total Attachments': len(attachments),
            'Source': 'Cached' if from_cache else 'Fresh Scan'
        }
        
        if from_cache and 'cached_at' in result:
            cached_time = result['cached_at'].strftime('%Y-%m-%d %H:%M')
            additional_info['Cached At'] = cached_time
        
        if 'scan_duration' in metadata and not from_cache:
            additional_info['Scan Time'] = f"{metadata['scan_duration']:.1f}s"
        
        # Configure the inventory view window
        window_config = {
            'title': 'Email Attachments',
            'columns': [
                {'key': 'Date', 'header': 'Date', 'width': 120, 'type': 'date'},
                {'key': 'From', 'header': 'From', 'width': 180, 'type': 'text'},
                {'key': 'Subject', 'header': 'Subject', 'width': 300, 'type': 'text'},
                {'key': 'AttachmentName', 'header': 'Attachment', 'width': 250, 'type': 'text'},
                {'key': 'Extension', 'header': 'Type', 'width': 60, 'type': 'text'},
                {'key': 'SizeFormatted', 'header': 'Size', 'width': 80, 'type': 'text'}
            ],
            'on_item_click': self._handle_item_click,  # New: single click handler
            'on_item_double_click': self._open_email,  # Keep for backward compatibility
            'show_stats': True,
            'allow_export': True,
            'window_width': 1200,
            'window_height': 600,
            'additional_info': additional_info
        }
        
        # Create custom inventory window with refresh button
        self.inventory_window = EmailInventoryWindow(
            self.parent, 
            attachments, 
            window_config,
            self.refresh_emails,
            self.full_refresh_emails
        )
    
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

    def refresh_emails(self):
        """Quick refresh - check for new emails only"""
        if self.inventory_window and hasattr(self.inventory_window, 'show_refreshing'):
            self.inventory_window.show_refreshing()
        
        # Run in background
        thread = threading.Thread(
            target=self._perform_quick_refresh,
            daemon=True
        )
        thread.start()
    
    def _perform_quick_refresh(self):
        """Perform quick refresh in background"""
        result = self.email_manager.refresh_recent_emails(hours_back=24)
        
        if self.inventory_window:
            self.inventory_window.after(0, lambda: self._update_inventory(result))
    
    def full_refresh_emails(self):
        """Full refresh - rescan all emails"""
        if self.inventory_window:
            self.inventory_window.destroy()
        self.show_email_attachments(force_refresh=True)
    
    def _update_inventory(self, result: dict):
        """Update inventory window with new data"""
        if self.inventory_window and self.inventory_window.winfo_exists():
            # Update the data
            self.inventory_window.original_data = result['data']
            self.inventory_window.filtered_data = result['data']
            self.inventory_window.populate_grid()
            self.inventory_window.update_stats()
            
            # Update additional info
            new_attachments = result.get('new_attachments', 0)
            if new_attachments > 0:
                self.inventory_window.show_refresh_complete(f"Found {new_attachments} new attachment(s)")
            else:
                self.inventory_window.show_refresh_complete("No new attachments found")
    
    def _open_email(self, email_data: dict):
        """Handle double-click on email item to open it"""
        if 'EntryID' in email_data:
            self.email_manager.open_email(email_data['EntryID'])
    
    def _show_no_emails_message(self):
        """Show a message when no emails with attachments are found"""
        WarningDialog.show(
            self.parent,
            "No Emails Found",
            f"No emails with attachments found in the last {self.email_manager.weeks_back} weeks."
        )
    
    def show_loading_dialog(self):
        """Show loading dialog during email scan"""
        self.loading_dialog = LoadingDialog(self.parent, "Scanning emails...")


class EmailInventoryWindow(InventoryViewWindow):
    """Extended inventory window with refresh capabilities"""
    
    def __init__(self, parent, data, config, quick_refresh_callback, full_refresh_callback):
        self.quick_refresh_callback = quick_refresh_callback
        self.full_refresh_callback = full_refresh_callback
        super().__init__(parent, data, config)
    
    def create_footer(self):
        """Override to add refresh buttons"""
        footer_frame = tk.Frame(self.content_frame, bg=Colors.DARK_GREEN, height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=2, pady=2)
        footer_frame.pack_propagate(False)
        
        # Left side - filter status and refresh status
        left_frame = tk.Frame(footer_frame, bg=Colors.DARK_GREEN)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.filter_status_label = tk.Label(left_frame, text="No filters applied", 
                                           bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                                           font=Fonts.MENU_ITEM)
        self.filter_status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Refresh status label
        self.refresh_status_label = tk.Label(left_frame, text="", 
                                           bg=Colors.DARK_GREEN, fg=Colors.LIGHT_GREEN,
                                           font=Fonts.MENU_ITEM)
        self.refresh_status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Right side - action buttons
        button_frame = tk.Frame(footer_frame, bg=Colors.DARK_GREEN)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Quick Refresh button
        quick_refresh_btn = tk.Button(button_frame, text="↻ Quick Refresh", 
                                     bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                                     relief=tk.RAISED, bd=1, cursor='hand2',
                                     font=Fonts.MENU_ITEM, padx=10,
                                     command=self.quick_refresh_callback)
        quick_refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Full Refresh button
        full_refresh_btn = tk.Button(button_frame, text="⟳ Full Refresh", 
                                    bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                                    relief=tk.RAISED, bd=1, cursor='hand2',
                                    font=Fonts.MENU_ITEM, padx=10,
                                    command=self.full_refresh_callback)
        full_refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Clear Filters
        clear_btn = tk.Button(button_frame, text="Clear All Filters", 
                             bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                             relief=tk.RAISED, bd=1, cursor='hand2',
                             font=Fonts.MENU_ITEM, padx=10,
                             command=self.clear_all_filters)
        clear_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Export to Excel
        if self.allow_export:
            export_btn = tk.Button(button_frame, text="Export to Excel", 
                                  bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                                  relief=tk.RAISED, bd=1, cursor='hand2',
                                  font=Fonts.MENU_ITEM, padx=10,
                                  command=self.export_to_excel)
            export_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Close button
        close_btn = tk.Button(button_frame, text="Close", 
                             bg=Colors.INACTIVE_GRAY, fg=Colors.WHITE,
                             relief=tk.RAISED, bd=1, cursor='hand2',
                             font=Fonts.MENU_ITEM, padx=10,
                             command=self.on_closing)
        close_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    def show_refreshing(self):
        """Show refreshing status"""
        self.refresh_status_label.config(text="Refreshing...")
    
    def show_refresh_complete(self, message: str):
        """Show refresh complete status"""
        self.refresh_status_label.config(text=message)
        # Clear message after 3 seconds
        self.after(3000, lambda: self.refresh_status_label.config(text=""))


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