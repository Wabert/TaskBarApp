# snip_feature.py
"""
Screen capture and document integration feature for SuiteView Taskbar
Handles taking screenshots and inserting them into Word documents or Outlook emails
"""

import os
import tempfile
import time
from datetime import datetime
from PIL import ImageGrab
import win32com.client
import pythoncom
from config import Colors, Fonts
from ui_components import ErrorDialog, WarningDialog
import tkinter as tk

class SnippingManager:
    """Manages screen capture and document integration"""
    
    def __init__(self, parent_window=None):
        self.parent_window = parent_window
        self.current_word_app = None
        self.current_word_doc = None
        self.current_outlook_app = None
        self.current_outlook_item = None
        self.temp_image_counter = 0
        
        # Create temp directory for screenshots
        self.temp_dir = os.path.join(tempfile.gettempdir(), "SuiteView_Screenshots")
        self.ensure_temp_directory()
    
    def ensure_temp_directory(self):
        """Ensure temporary directory exists for storing screenshots"""
        try:
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)
        except Exception as e:
            print(f"Warning: Could not create temp directory: {e}")
            self.temp_dir = tempfile.gettempdir()
    
    def capture_primary_screen(self):
        """Capture screenshot of primary monitor and save to temp file"""
        try:
            # Capture the primary screen
            screenshot = ImageGrab.grab()
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.temp_image_counter += 1
            filename = f"screenshot_{timestamp}_{self.temp_image_counter}.png"
            filepath = os.path.join(self.temp_dir, filename)
            
            # Save screenshot
            screenshot.save(filepath, "PNG")
            print(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            self._show_error("Screenshot Error", f"Failed to capture screenshot: {str(e)}")
            return None
    
    def snip_to_target(self, target_app="Word"):
        """Main method to handle snipping to specified application"""
        try:
            # Capture screenshot first
            image_path = self.capture_primary_screen()
            if not image_path:
                return False
            
            # Route to appropriate handler
            if target_app.lower() == "word":
                return self.snip_to_word(image_path)
            elif target_app.lower() == "outlook":
                return self.snip_to_outlook(image_path)
            else:
                self._show_error("Invalid Target", f"Unknown target application: {target_app}")
                return False
                
        except Exception as e:
            self._show_error("Snip Error", f"Failed to complete snip operation: {str(e)}")
            return False
    
    def snip_to_word(self, image_path):
        """Insert screenshot into Word document"""
        try:
            # Check if we have an active Word document
            if not self._is_word_document_active():
                # Create new Word document
                if not self._create_new_word_document():
                    return False
            
            # Insert image into document
            if self._insert_image_to_word(image_path):
                print("Successfully added screenshot to Word document")
                return True
            else:
                return False
                
        except Exception as e:
            self._show_error("Word Error", f"Failed to add screenshot to Word: {str(e)}")
            return False
    
    def snip_to_outlook(self, image_path):
        """Insert screenshot into Outlook email"""
        try:
            # Check if we have an active Outlook email
            if not self._is_outlook_email_active():
                # Create new Outlook email
                if not self._create_new_outlook_email():
                    return False
            
            # Insert image into email
            if self._insert_image_to_outlook(image_path):
                print("Successfully added screenshot to Outlook email")
                return True
            else:
                return False
                
        except Exception as e:
            self._show_error("Outlook Error", f"Failed to add screenshot to Outlook: {str(e)}")
            return False
    
    def _is_word_document_active(self):
        """Check if the current Word document is still active"""
        try:
            if not self.current_word_app or not self.current_word_doc:
                return False
            
            # Try to access the document - this will fail if it's closed
            _ = self.current_word_doc.Name
            
            # Check if the document is still in the application's documents collection
            for doc in self.current_word_app.Documents:
                if doc.Name == self.current_word_doc.Name:
                    return True
            
            return False
            
        except Exception:
            # If any error occurs, assume document is no longer active
            self.current_word_doc = None
            return False
    
    def _is_outlook_email_active(self):
        """Check if the current Outlook email is still active"""
        try:
            if not self.current_outlook_app or not self.current_outlook_item:
                return False
            
            # Try to access the email item - this will fail if it's closed/sent
            _ = self.current_outlook_item.Subject
            return True
            
        except Exception:
            # If any error occurs, assume email is no longer active
            self.current_outlook_item = None
            return False
    
    def _create_new_word_document(self):
        """Create a new Word document"""
        try:
            # Initialize COM
            pythoncom.CoInitialize()
            
            # Connect to or create Word application
            try:
                self.current_word_app = win32com.client.GetActiveObject("Word.Application")
            except:
                self.current_word_app = win32com.client.Dispatch("Word.Application")
            
            # Make Word visible
            self.current_word_app.Visible = True
            
            # Create new document
            self.current_word_doc = self.current_word_app.Documents.Add()
            
            # Add a title
            title_range = self.current_word_doc.Range(0, 0)
            title_range.Text = f"Screenshots - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n\n"
            title_range.Font.Bold = True
            title_range.Font.Size = 14
            
            # Move cursor to end for image insertion
            # Use numeric constant instead of named constant to avoid import issues
            self.current_word_doc.Range().Collapse(0)  # 0 = wdCollapseEnd
            
            print("Created new Word document")
            return True
            
        except Exception as e:
            self._show_error("Word Creation Error", f"Failed to create Word document: {str(e)}")
            self.current_word_app = None
            self.current_word_doc = None
            return False
    
    def _create_new_outlook_email(self):
        """Create a new Outlook email"""
        try:
            # Initialize COM
            pythoncom.CoInitialize()
            
            # Connect to Outlook
            try:
                self.current_outlook_app = win32com.client.GetActiveObject("Outlook.Application")
            except:
                self.current_outlook_app = win32com.client.Dispatch("Outlook.Application")
            
            # Create new mail item
            self.current_outlook_item = self.current_outlook_app.CreateItem(0)  # 0 = olMailItem
            
            # Set email properties
            self.current_outlook_item.Subject = f"Screenshots - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"
            self.current_outlook_item.Body = "Screenshots captured:\n\n"
            
            # Display the email
            self.current_outlook_item.Display()
            
            print("Created new Outlook email")
            return True
            
        except Exception as e:
            self._show_error("Outlook Creation Error", f"Failed to create Outlook email: {str(e)}")
            self.current_outlook_app = None
            self.current_outlook_item = None
            return False
    
    def _insert_image_to_word(self, image_path):
        """Insert image into the current Word document"""
        try:
            if not self.current_word_doc:
                return False
            
            # Always position at the end of the document to preserve the title
            doc_end = self.current_word_doc.Range()
            doc_end.Collapse(0)  # 0 = wdCollapseEnd
            doc_end.Select()
            
            # Get the selection at the end of the document
            selection = self.current_word_app.Selection
            
            # Add timestamp before image
            timestamp_text = f"Screenshot taken: {datetime.now().strftime('%I:%M:%S %p')}\n"
            selection.TypeText(timestamp_text)
            
            # Insert the image
            inline_shape = selection.InlineShapes.AddPicture(
                FileName=image_path,
                LinkToFile=False,
                SaveWithDocument=True
            )
            
            # Scale image to fit page width (optional)
            page_width = self.current_word_doc.PageSetup.PageWidth - \
                        self.current_word_doc.PageSetup.LeftMargin - \
                        self.current_word_doc.PageSetup.RightMargin
            
            if inline_shape.Width > page_width:
                scale_factor = page_width / inline_shape.Width
                inline_shape.Width = page_width
                inline_shape.Height = inline_shape.Height * scale_factor
            
            # Add some space after the image
            selection.TypeText("\n\n")
            
            # Clean up temp file
            self._cleanup_temp_file(image_path)
            
            return True
            
        except Exception as e:
            print(f"Error inserting image to Word: {e}")
            return False
    
    def _insert_image_to_outlook(self, image_path):
        """Insert image into the current Outlook email"""
        try:
            if not self.current_outlook_item:
                return False
            
            # Get the current body and add timestamp
            current_body = self.current_outlook_item.Body if self.current_outlook_item.Body else ""
            timestamp_text = f"Screenshot taken: {datetime.now().strftime('%I:%M:%S %p')}\n"
            
            # Add the image as an attachment and embed it
            attachment = self.current_outlook_item.Attachments.Add(image_path)
            
            # For HTML emails, we could embed the image inline, but for simplicity
            # we'll just attach it and add a note in the body
            self.current_outlook_item.Body = current_body + timestamp_text + "[Screenshot attached]\n\n"
            
            # Clean up temp file
            self._cleanup_temp_file(image_path)
            
            return True
            
        except Exception as e:
            print(f"Error inserting image to Outlook: {e}")
            return False
    
    def _cleanup_temp_file(self, filepath):
        """Clean up temporary image file"""
        try:
            # Wait a moment to ensure file is not locked
            time.sleep(0.1)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Warning: Could not delete temp file {filepath}: {e}")
    
    def _show_error(self, title, message):
        """Show error dialog to user"""
        print(f"Error - {title}: {message}")
        if self.parent_window:
            try:
                ErrorDialog.show(self.parent_window, title, message)
            except:
                pass  # Fallback to console output only
    
    def cleanup_temp_directory(self):
        """Clean up old temporary files"""
        try:
            if os.path.exists(self.temp_dir):
                for filename in os.listdir(self.temp_dir):
                    if filename.startswith("screenshot_"):
                        filepath = os.path.join(self.temp_dir, filename)
                        # Delete files older than 1 hour
                        if time.time() - os.path.getctime(filepath) > 3600:
                            os.remove(filepath)
        except Exception as e:
            print(f"Warning: Could not clean temp directory: {e}")
    
    def force_new_document(self, target_app="Word"):
        """Force creation of a new document (useful for manual reset)"""
        if target_app.lower() == "word":
            self.current_word_doc = None
            self.current_word_app = None
        elif target_app.lower() == "outlook":
            self.current_outlook_item = None
            self.current_outlook_app = None

class SnipUI:
    """UI components for the Snip feature"""
    
    @staticmethod
    def create_snip_button(parent, snipping_manager, target_var):
        """Create the Snip button"""
        def on_snip_click():
            target = target_var.get()
            success = snipping_manager.snip_to_target(target)
            if success:
                print(f"Screenshot successfully added to {target}")
        
        snip_btn = tk.Button(parent, text="Snip", 
                           bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                           relief=tk.FLAT, font=Fonts.TASKBAR_BUTTON, 
                           cursor='hand2', activebackground=Colors.HOVER_GREEN, 
                           bd=0, padx=15, command=on_snip_click)
        return snip_btn
    
    @staticmethod
    def create_target_combobox(parent, default_value="Word"):
        """Create the target application combobox"""
        from tkinter import ttk
        
        target_var = tk.StringVar(value=default_value)
        combo = ttk.Combobox(parent, textvariable=target_var, 
                           values=["Word", "Outlook"],
                           state='readonly', width=8)
        
        # Style the combobox to match the app theme
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Snip.TCombobox', 
                       fieldbackground=Colors.MEDIUM_GREEN, 
                       background=Colors.MEDIUM_GREEN)
        combo.configure(style='Snip.TCombobox')
        
        return combo, target_var

# Integration helper functions for taskbar.py
def add_snip_feature_to_taskbar(taskbar_instance):
    """Add Snip feature to the existing taskbar"""
    
    # Create snipping manager
    snipping_manager = SnippingManager(taskbar_instance.root)
    
    # Create frame for snip controls
    snip_frame = tk.Frame(taskbar_instance.main_frame, bg=Colors.DARK_GREEN)
    snip_frame.pack(side=tk.LEFT, padx=10)
    
    # Create target selection combobox
    combo, target_var = SnipUI.create_target_combobox(snip_frame)
    combo.pack(side=tk.LEFT, padx=(0, 5))
    
    # Create snip button
    snip_btn = SnipUI.create_snip_button(snip_frame, snipping_manager, target_var)
    snip_btn.pack(side=tk.LEFT)
    
    # Store reference for cleanup
    taskbar_instance.snipping_manager = snipping_manager
    
    # Schedule periodic cleanup of temp files
    def cleanup_temp_files():
        snipping_manager.cleanup_temp_directory()
        taskbar_instance.root.after(300000, cleanup_temp_files)  # Every 5 minutes
    
    taskbar_instance.root.after(300000, cleanup_temp_files)
    
    return snipping_manager