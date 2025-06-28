# email_manager.py
"""
Enhanced email attachment management with caching functionality
Stores email scans for quick retrieval and supports multiple scan types
"""

import win32com.client
from datetime import datetime, timedelta
import tkinter as tk
import json
import os
from pathlib import Path
import threading
import time

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
    """Enhanced email manager with caching and multiple scan types"""
    
    # Scan type constants
    SCAN_ATTACHMENTS = "attachments"
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
                                   force_refresh: bool = False) -> dict:
        """
        Get emails with attachments, using cache if available
        
        Returns:
            Dictionary with 'data', 'metadata', and 'from_cache' keys
        """
        scan_type = self.SCAN_ATTACHMENTS
        
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
        return self._scan_emails_with_attachments()
    
    def _scan_emails_with_attachments(self) -> dict:
        """Perform a fresh scan for emails with attachments - one line per attachment"""
        
        start_time = datetime.now()
        email_attachments = []  # Changed from emails_with_attachments
        
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
                                    'AttachmentIndex': i,  # Store which attachment this is
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

    def refresh_recent_emails(self, hours_back: int = 24) -> dict:
        """
        Quick refresh to get only recent emails (last N hours)
        Updates the cache with new emails - one line per attachment
        """
        if not self.outlook:
            self._initialize_outlook()
            
        if not self.outlook:
            return {'data': [], 'metadata': {}, 'from_cache': False}
        
        # Load existing cache
        cached_data = self.cache.load_scan(self.SCAN_ATTACHMENTS)
        existing_attachments = cached_data['data'] if cached_data else []
        
        # Create a set of existing entries to avoid duplicates
        # Use EntryID + AttachmentIndex as unique key
        existing_keys = {
            f"{att['EntryID']}_{att.get('AttachmentIndex', 0)}" 
            for att in existing_attachments
        }
        
        # Scan only recent emails
        start_time = datetime.now()
        new_attachments = []
        
        try:
            inbox = self.outlook.GetDefaultFolder(6)
            messages = inbox.Items
            
            # Filter for very recent messages
            start_date = datetime.now() - timedelta(hours=hours_back)
            date_filter = f"[ReceivedTime] >= '{start_date.strftime('%m/%d/%Y %H:%M %p')}'"
            messages = messages.Restrict(date_filter)
            
            new_emails_count = 0
            
            for message in messages:
                try:
                    if message.Attachments.Count > 0:
                        email_found = False
                        
                        # Process each attachment
                        for i in range(1, message.Attachments.Count + 1):
                            unique_key = f"{message.EntryID}_{i}"
                            
                            # Skip if already in cache
                            if unique_key in existing_keys:
                                continue
                            
                            email_found = True
                            
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
                                new_attachments.append(attachment_data)
                                
                            except Exception as e:
                                print(f"Error processing attachment: {e}")
                        
                        if email_found:
                            new_emails_count += 1
                            
                except Exception as e:
                    print(f"Error processing new message: {e}")
                    continue
            
            # Merge with existing attachments
            all_attachments = new_attachments + existing_attachments
            all_attachments.sort(key=lambda x: x['ReceivedTime'], reverse=True)
            
            # Update metadata
            metadata = cached_data['metadata'] if cached_data else {}
            metadata['last_refresh'] = datetime.now().isoformat()
            metadata['new_emails_found'] = new_emails_count
            metadata['new_attachments_found'] = len(new_attachments)
            metadata['total_attachment_lines'] = len(all_attachments)
            
            # Save updated cache
            self.cache.save_scan(self.SCAN_ATTACHMENTS, all_attachments, metadata)
            
            return {
                'data': all_attachments,
                'metadata': metadata,
                'from_cache': False,
                'new_attachments': len(new_attachments)
            }
            
        except Exception as e:
            print(f"Error refreshing emails: {e}")
            return {'data': existing_attachments, 'metadata': {}, 'from_cache': True}

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