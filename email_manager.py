# email_manager.py
"""
Updated email attachment management with support for both received and sent emails
"""

import win32com.client
from datetime import datetime, timedelta
import tkinter as tk
import json
import os
from pathlib import Path
import threading
import time

# Keep existing EmailCache class as-is
class EmailCache:
    """Handles caching of email scan results"""
    
    def __init__(self, cache_dir: str | Path = None):
        """Initialize the email cache"""
        if cache_dir is None:
            # Use app config directory
            self.cache_dir = Path.home() / '.suiteview' / 'email_cache'
        else:
            self.cache_dir = cache_dir
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_file(self, scan_type: str) -> Path:
        """Get the cache file path for a specific scan type"""
        return self.cache_dir / f"{scan_type}_cache.json"
    
    def save_scan(self, scan_type: str, data: list[dict], metadata: dict):
        """Save scan results to cache"""
        cache_file = self.get_cache_file(scan_type)
        cache_data = {
            'metadata': metadata,
            'data': data,
            'cached_at': datetime.now().isoformat()
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving cache: {e}")
            return False
    
    def load_scan(self, scan_type: str) -> dict | None:
        """Load scan results from cache"""
        cache_file = self.get_cache_file(scan_type)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Convert cached_at back to datetime
            cache_data['cached_at'] = datetime.fromisoformat(cache_data['cached_at'])
            return cache_data
        except Exception as e:
            print(f"Error loading cache: {e}")
            return None
    
    def is_cache_valid(self, scan_type: str, max_age_minutes: int = 60) -> bool:
        """Check if cache exists and is still valid"""
        cache_data = self.load_scan(scan_type)
        if not cache_data:
            return False
        
        cached_at = cache_data['cached_at']
        age = datetime.now() - cached_at
        return age.total_seconds() < (max_age_minutes * 60)
    
    def clear_cache(self, scan_type: str | None = None):
        """Clear cache for specific scan type or all caches"""
        if scan_type:
            cache_file = self.get_cache_file(scan_type)
            if cache_file.exists():
                cache_file.unlink()
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*_cache.json"):
                cache_file.unlink()


class EmailManager:
    """Enhanced email manager with caching and support for received/sent emails"""
    
    # Scan type constants
    SCAN_ATTACHMENTS = "attachments"
    SCAN_ATTACHMENTS_SENT = "attachments_sent"
    SCAN_IMPORTANT = "important"
    SCAN_FLAGGED = "flagged"
    SCAN_UNREAD = "unread"
    
    def __init__(self, weeks_back: int = 2):
        """Initialize the email manager"""
        self.weeks_back = weeks_back
        self.outlook = None
        self.cache = EmailCache()
        self._initialize_outlook()
        
        # Track if a scan is in progress
        self.scan_in_progress = False
        self.current_scan_thread = None
    
    def _initialize_outlook(self):
        """Initialize Outlook connection"""
        try:
            self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        except Exception as e:
            print(f"Error initializing Outlook: {e}")
            self.outlook = None
    
    def get_emails_with_attachments(self, use_cache: bool = True, 
                                   force_refresh: bool = False,
                                   email_type: str = 'received') -> dict:
        """
        Get emails with attachments, using cache if available
        
        Args:
            use_cache: Whether to use cached data
            force_refresh: Force a fresh scan
            email_type: 'received' or 'sent'
        
        Returns:
            Dictionary with 'data', 'metadata', and 'from_cache' keys
        """
        scan_type = self.SCAN_ATTACHMENTS if email_type == 'received' else self.SCAN_ATTACHMENTS_SENT
        
        # Check cache first if requested
        if use_cache and not force_refresh:
            cached_data = self.cache.load_scan(scan_type)
            if cached_data and self.cache.is_cache_valid(scan_type):
                return {
                    'data': cached_data['data'],
                    'metadata': cached_data['metadata'],
                    'from_cache': True,
                    'cached_at': cached_data['cached_at']
                }
        
        # Perform fresh scan
        if email_type == 'received':
            return self._scan_emails_with_attachments()
        else:
            return self._scan_sent_emails_with_attachments()
    
    def _scan_sent_emails_with_attachments(self) -> dict:
        """Scan sent emails for attachments"""
        start_time = datetime.now()
        email_attachments = []
        
        try:
            # Create a new Outlook instance for this thread
            import pythoncom
            pythoncom.CoInitialize()
            
            # Create fresh Outlook connection for this scan
            outlook_app = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook_app.GetNamespace("MAPI")
            
            # Get the Sent Items folder (5 = olFolderSentMail)
            sent_folder = namespace.GetDefaultFolder(5)
            messages = sent_folder.Items
            
            # Filter messages by date
            start_date = datetime.now() - timedelta(weeks=self.weeks_back)
            date_filter = f"[SentOn] >= '{start_date.strftime('%m/%d/%Y %H:%M %p')}'"
            messages = messages.Restrict(date_filter)
            
            total_scanned = 0
            total_emails_with_attachments = 0
            
            for message in messages:
                total_scanned += 1
                try:
                    if message.Attachments.Count > 0:
                        total_emails_with_attachments += 1
                        
                        # Get recipients
                        recipients = []
                        for i in range(1, message.Recipients.Count + 1):
                            try:
                                recipient = message.Recipients.Item(i)
                                recipients.append(recipient.Name)
                            except:
                                pass
                        to_string = "; ".join(recipients) if recipients else "Unknown"
                        
                        # Create one entry per attachment
                        for i in range(1, message.Attachments.Count + 1):
                            try:
                                attachment = message.Attachments.Item(i)
                                attachment_name = attachment.FileName
                                
                                # Get file extension
                                if '.' in attachment_name:
                                    extension = attachment_name.rsplit('.', 1)[1].upper()
                                else:
                                    extension = 'NONE'
                                
                                # Try to get size
                                try:
                                    attachment_size = attachment.Size
                                except:
                                    attachment_size = 0
                                
                                attachment_data = {
                                    'Date': message.SentOn.strftime("%Y-%m-%d %H:%M"),
                                    'To': to_string,  # Changed from 'From' to 'To'
                                    'Subject': message.Subject,
                                    'AttachmentName': attachment_name,
                                    'Extension': extension,
                                    'Size': attachment_size,
                                    'SizeFormatted': self._format_size(attachment_size) if attachment_size > 0 else "Unknown",
                                    'EntryID': message.EntryID,
                                    'AttachmentIndex': i,
                                    'SentOn': message.SentOn.isoformat(),
                                }
                                email_attachments.append(attachment_data)
                                
                            except Exception as e:
                                print(f"Error processing attachment {i}: {e}")
                                # Still add an entry for failed attachments
                                attachment_data = {
                                    'Date': message.SentOn.strftime("%Y-%m-%d %H:%M"),
                                    'To': to_string,
                                    'Subject': message.Subject,
                                    'AttachmentName': "(Error reading attachment)",
                                    'Extension': 'ERROR',
                                    'Size': 0,
                                    'SizeFormatted': "Error",
                                    'EntryID': message.EntryID,
                                    'AttachmentIndex': i,
                                    'SentOn': message.SentOn.isoformat(),
                                }
                                email_attachments.append(attachment_data)
                                
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue
            
            # Sort by date, newest first
            email_attachments.sort(key=lambda x: x['SentOn'], reverse=True)
            
            # Prepare metadata
            metadata = {
                'scan_type': self.SCAN_ATTACHMENTS_SENT,
                'weeks_back': self.weeks_back,
                'start_date': start_date.isoformat(),
                'end_date': datetime.now().isoformat(),
                'total_scanned': total_scanned,
                'total_emails_with_attachments': total_emails_with_attachments,
                'total_attachment_lines': len(email_attachments),
                'scan_duration': (datetime.now() - start_time).total_seconds()
            }
            
            # Save to cache
            self.cache.save_scan(self.SCAN_ATTACHMENTS_SENT, email_attachments, metadata)
            
            return {
                'data': email_attachments,
                'metadata': metadata,
                'from_cache': False
            }
        
        except Exception as e:
            print(f"Error retrieving sent emails: {e}")
            return {'data': [], 'metadata': {}, 'from_cache': False}
            
        finally:
            # Uninitialize COM for this thread
            try:
                pythoncom.CoUninitialize()
            except:
                pass
    
    def _scan_emails_with_attachments(self) -> dict:
        """Perform a fresh scan for emails with attachments - one line per attachment"""
        
        start_time = datetime.now()
        email_attachments = []
        
        try:
            # Create a new Outlook instance for this thread
            import pythoncom
            pythoncom.CoInitialize()
            
            # Create fresh Outlook connection for this scan
            outlook_app = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook_app.GetNamespace("MAPI")
            
            # Try to get the default inbox
            inbox = namespace.GetDefaultFolder(6)  # 6 = olFolderInbox
            messages = inbox.Items
            
            # Filter messages by date
            start_date = datetime.now() - timedelta(weeks=self.weeks_back)
            date_filter = f"[ReceivedTime] >= '{start_date.strftime('%m/%d/%Y %H:%M %p')}'"
            messages = messages.Restrict(date_filter)
            
            total_scanned = 0
            total_emails_with_attachments = 0
            
            for message in messages:
                total_scanned += 1
                try:
                    if message.Attachments.Count > 0:
                        total_emails_with_attachments += 1
                        
                        # Create one entry per attachment
                        for i in range(1, message.Attachments.Count + 1):
                            try:
                                attachment = message.Attachments.Item(i)
                                attachment_name = attachment.FileName
                                
                                # Get file extension
                                if '.' in attachment_name:
                                    extension = attachment_name.rsplit('.', 1)[1].upper()
                                else:
                                    extension = 'NONE'
                                
                                # Try to get size
                                try:
                                    attachment_size = attachment.Size
                                except:
                                    attachment_size = 0
                                
                                attachment_data = {
                                    'Date': message.ReceivedTime.strftime("%Y-%m-%d %H:%M"),
                                    'From': message.SenderName,
                                    'Subject': message.Subject,
                                    'AttachmentName': attachment_name,
                                    'Extension': extension,
                                    'Size': attachment_size,
                                    'SizeFormatted': self._format_size(attachment_size) if attachment_size > 0 else "Unknown",
                                    'EntryID': message.EntryID,
                                    'AttachmentIndex': i,
                                    'ReceivedTime': message.ReceivedTime.isoformat(),
                                }
                                email_attachments.append(attachment_data)
                                
                            except Exception as e:
                                print(f"Error processing attachment {i}: {e}")
                                # Still add an entry for failed attachments
                                attachment_data = {
                                    'Date': message.ReceivedTime.strftime("%Y-%m-%d %H:%M"),
                                    'From': message.SenderName,
                                    'Subject': message.Subject,
                                    'AttachmentName': "(Error reading attachment)",
                                    'Extension': 'ERROR',
                                    'Size': 0,
                                    'SizeFormatted': "Error",
                                    'EntryID': message.EntryID,
                                    'AttachmentIndex': i,
                                    'ReceivedTime': message.ReceivedTime.isoformat(),
                                }
                                email_attachments.append(attachment_data)
                                
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue
            
            # Sort by date, newest first
            email_attachments.sort(key=lambda x: x['ReceivedTime'], reverse=True)
            
            # Prepare metadata
            metadata = {
                'scan_type': self.SCAN_ATTACHMENTS,
                'weeks_back': self.weeks_back,
                'start_date': start_date.isoformat(),
                'end_date': datetime.now().isoformat(),
                'total_scanned': total_scanned,
                'total_emails_with_attachments': total_emails_with_attachments,
                'total_attachment_lines': len(email_attachments),
                'scan_duration': (datetime.now() - start_time).total_seconds()
            }
            
            # Save to cache
            self.cache.save_scan(self.SCAN_ATTACHMENTS, email_attachments, metadata)
            
            return {
                'data': email_attachments,
                'metadata': metadata,
                'from_cache': False
            }
        
        except Exception as e:
            print(f"Error retrieving emails: {e}")
            return {'data': [], 'metadata': {}, 'from_cache': False}
            
        finally:
            # Uninitialize COM for this thread
            try:
                pythoncom.CoUninitialize()
            except:
                pass
    
    def open_attachment(self, entry_id: str, attachment_index: int):
        """Open a specific attachment from an email"""
        if not self.outlook:
            self._initialize_outlook()
            
        if not self.outlook:
            print("Cannot connect to Outlook")
            return
        
        try:
            import tempfile
            import os
            
            outlook_app = win32com.client.Dispatch("Outlook.Application")
            mail_item = outlook_app.Session.GetItemFromID(entry_id)
            
            if attachment_index <= mail_item.Attachments.Count:
                attachment = mail_item.Attachments.Item(attachment_index)
                
                # Save attachment to temp directory
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, attachment.FileName)
                attachment.SaveAsFile(temp_path)
                
                # Open the file
                os.startfile(temp_path)
            else:
                print(f"Attachment index {attachment_index} not found")
                
        except Exception as e:
            print(f"Error opening attachment: {e}")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        if i == 0:
            return f"{int(size)} {size_names[i]}"
        else:
            return f"{size:.1f} {size_names[i]}"
    
    def open_email(self, entry_id: str):
        """Open a specific email in Outlook"""
        if not self.outlook:
            return
        
        try:
            outlook_app = win32com.client.Dispatch("Outlook.Application")
            mail_item = outlook_app.Session.GetItemFromID(entry_id)
            mail_item.Display()
        except Exception as e:
            print(f"Error opening email: {e}")
    
    def clear_cache(self, scan_type: str | None = None):
        """Clear email cache"""
        self.cache.clear_cache(scan_type)
    
    def get_cache_info(self, scan_type: str) -> dict | None:
        """Get information about cached data"""
        cached_data = self.cache.load_scan(scan_type)
        if not cached_data:
            return None
        
        return {
            'cached_at': cached_data['cached_at'],
            'item_count': len(cached_data['data']),
            'metadata': cached_data['metadata']
        }