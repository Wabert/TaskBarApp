# browse_choice_dialog.py
"""
Custom dialog for choosing between file and folder browsing
Replaces messagebox with properly styled, topmost dialog
"""

import tkinter as tk
from tkinter import filedialog
from ..core.config import Colors, Fonts, Dimensions
from ..ui.ui_components import CustomDialog

class BrowseChoiceDialog(CustomDialog):
    """Custom dialog for choosing between File or Folder browsing"""
    
    def __init__(self, parent):
        super().__init__(parent, "Browse Type", width=350, height=350)
        
        self.choice_result = None  # Will store 'file', 'folder', or None
        self.selected_path = None  # Will store the selected path
        
        # Make sure dialog stays on top of everything
        self.attributes('-topmost', True)
        self.lift()
        self.focus_force()
        
        self.create_content()
        self.create_buttons()
        
        # Bind keyboard shortcuts
        self.bind('<F>', lambda e: self.choose_file())
        self.bind('<f>', lambda e: self.choose_file())
        self.bind('<D>', lambda e: self.choose_folder())
        self.bind('<d>', lambda e: self.choose_folder())
        self.bind('<Escape>', lambda e: self.cancel())
    
    def create_content(self):
        """Create the dialog content"""
        # Icon
        icon_label = tk.Label(self.dialog_content, text="📁", bg=Colors.LIGHT_GREEN,
                             fg=Colors.DARK_GREEN, font=('Arial', 24))
        icon_label.pack(pady=10)
        
        # Main message
        message_label = tk.Label(self.dialog_content, 
                               text="What would you like to browse for?", 
                               bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                               font=Fonts.DIALOG_LABEL, wraplength=300)
        message_label.pack(pady=5)
        
        # Instructions
        instruction_label = tk.Label(self.dialog_content, 
                                   text="Choose File for documents, applications, etc.\nChoose Folder for directories", 
                                   bg=Colors.LIGHT_GREEN, fg=Colors.DARK_GREEN,
                                   font=(Fonts.DIALOG_LABEL[0], Fonts.DIALOG_LABEL[1] - 1),
                                   justify=tk.CENTER)
        instruction_label.pack(pady=5)
    
    def create_buttons(self):
        """Create the choice buttons"""
        # Make sure button frame is visible and has proper height
        self.button_frame.configure(height=80)
        self.button_frame.pack_propagate(False)
        
        button_container = tk.Frame(self.button_frame, bg=Colors.LIGHT_GREEN)
        button_container.pack(expand=True, fill=tk.BOTH, pady=10)
        
        # File button (primary choice)
        file_btn = tk.Button(button_container, text="File", 
                           bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                           command=self.choose_file, 
                           width=10, height=20,
                           font=Fonts.DIALOG_BUTTON, 
                           relief=tk.RAISED, bd=2,
                           cursor='hand2')
        file_btn.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Folder button
        folder_btn = tk.Button(button_container, text="Folder", 
                             bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                             command=self.choose_folder, 
                             width=10, height=20,
                             font=Fonts.DIALOG_BUTTON, 
                             relief=tk.RAISED, bd=2,
                             cursor='hand2')
        folder_btn.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Cancel button
        cancel_btn = tk.Button(button_container, text="Cancel", 
                             bg=Colors.INACTIVE_GRAY, fg=Colors.WHITE,
                             command=self.cancel, 
                             width=8, height=20,
                             font=Fonts.DIALOG_BUTTON, 
                             relief=tk.RAISED, bd=1)
        cancel_btn.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Set focus on File button (most common choice)
        file_btn.focus_set()
    
    def choose_file(self):
        """Handle file selection"""
        self.choice_result = 'file'
        
        # Disable topmost and hide this dialog temporarily
        self.attributes('-topmost', False)
        self.withdraw()  # Hide this dialog temporarily
        
        # Use the parent window for the file dialog
        try:
            path = filedialog.askopenfilename(
                parent=self.parent,
                title="Select File",
                filetypes=[
                    ("All Files", "*.*"),
                    ("Executables", "*.exe"),
                    ("Documents", "*.pdf;*.doc;*.docx;*.txt"),
                    ("Spreadsheets", "*.xls;*.xlsx;*.csv"),
                    ("Images", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")
                ]
            )
            
            if path:
                self.selected_path = path
                self.result = True
            else:
                self.result = None
                
        except Exception as e:
            print(f"Error in file dialog: {e}")
            self.result = None
        
        self.destroy()
    
    def choose_folder(self):
        """Handle folder selection"""
        self.choice_result = 'folder'
                
        # Disable topmost and hide this dialog temporarily
        self.attributes('-topmost', False)
        self.withdraw()  # Hide this dialog temporarily
        
        # Use the parent window for the folder dialog
        try:
            path = filedialog.askdirectory(
                parent=self.parent,
                title="Select Folder"
            )
            
            if path:
                self.selected_path = path
                self.result = True
            else:
                self.result = None
                
        except Exception as e:
            print(f"Error in folder dialog: {e}")
            self.result = None
        
        self.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.choice_result = None
        self.selected_path = None
        self.result = None
        self.destroy()
    
    @classmethod
    def get_path(cls, parent):
        """
        Show the browse choice dialog and return the selected path
        
        Returns:
            tuple: (choice_type, selected_path) where choice_type is 'file', 'folder', or None
        """
        dialog = cls(parent)
        
        # Ensure dialog is visible and on top
        dialog.deiconify()
        dialog.lift()
        dialog.attributes('-topmost', True)
        dialog.focus_force()
        dialog.grab_set()
        
        # Wait for dialog to complete
        parent.wait_window(dialog)
        
        return dialog.choice_result, dialog.selected_path