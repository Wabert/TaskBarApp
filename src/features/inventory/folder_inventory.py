# folder_inventory.py
"""
Folder Inventory feature for SuiteView Taskbar Application
Provides dialog for configuration and tree view of folder contents
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import threading
from ...ui.window_base import SimpleWindow, InventoryViewWindow
from ...core.config import Colors, Fonts
from ...utils.explorer_utils import ExplorerDetector

class FolderInventoryDialog(SimpleWindow):
    """Dialog for configuring folder inventory scan using SimpleWindow"""
    
    def __init__(self, parent):
        # Initialize SimpleWindow without resize handles
        super().__init__(parent, "Folder Inventory", resize_handles=None)
        
        # Set background color to light green
        self.content_frame.configure(bg=Colors.LIGHT_GREEN)
        
        # Set window size
        self.geometry("500x350")
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 350) // 2
        self.geometry(f"500x350+{x}+{y}")
        
        # Set background color to light green
        self.content_frame.configure(bg=Colors.LIGHT_GREEN)
        
        self.selected_folder = ""
        self.scan_thread = None
        self.cancel_scan = False
        self.inventory_data = []
        
        self._create_content()
        
        # Auto-populate folder field
        self.auto_populate_folder()
        
        # Set focus on folder field
        self.folder_entry.focus_set()
    
    def _create_content(self):
        """Create the dialog content"""
        content = self.content_frame
        
        # Folder selection
        folder_frame = tk.Frame(content, bg=Colors.LIGHT_GREEN)
        folder_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        tk.Label(folder_frame, text="Folder to scan:", 
                bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                font=Fonts.DIALOG_LABEL).pack(anchor='w')
        
        folder_input_frame = tk.Frame(folder_frame, bg=Colors.LIGHT_GREEN)
        folder_input_frame.pack(fill='x', pady=(5, 0))
        
        self.folder_var = tk.StringVar()
        self.folder_entry = tk.Entry(folder_input_frame, textvariable=self.folder_var,
                                    font=Fonts.DIALOG_LABEL, bg='white')
        self.folder_entry.pack(side='left', fill='x', expand=True)
        
        browse_btn = tk.Button(folder_input_frame, text="Browse...", 
                             command=self.browse_folder,
                             bg=Colors.DARK_GREEN, fg='white',
                             font=Fonts.BUTTON, relief='flat',
                             cursor='hand2', padx=10)
        browse_btn.pack(side='right', padx=(5, 0))
        
        # Scan depth option
        depth_frame = tk.Frame(content, bg=Colors.LIGHT_GREEN)
        depth_frame.pack(fill='x', padx=10, pady=(20, 0))
        
        tk.Label(depth_frame, text="Scan Depth:", 
                bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                font=Fonts.DIALOG_LABEL).pack(anchor='w')
        
        self.depth_var = tk.IntVar(value=0)
        
        depth_options = tk.Frame(depth_frame, bg=Colors.LIGHT_GREEN)
        depth_options.pack(fill='x', pady=(5, 0))
        
        tk.Radiobutton(depth_options, text="1 level", variable=self.depth_var, value=0,
                      bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                      font=Fonts.DIALOG_LABEL,
                      selectcolor=Colors.LIGHT_GREEN).pack(side='left')
        
        tk.Radiobutton(depth_options, text="2 level", variable=self.depth_var, value=1,
                      bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                      font=Fonts.DIALOG_LABEL,
                      selectcolor=Colors.LIGHT_GREEN).pack(side='left', padx=(20, 0))
        
        tk.Radiobutton(depth_options, text="All levels", variable=self.depth_var, value=2,
                      bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                      font=Fonts.DIALOG_LABEL,
                      selectcolor=Colors.LIGHT_GREEN).pack(side='left', padx=(20, 0))

       

        # Content type option
        content_frame = tk.Frame(content, bg=Colors.LIGHT_GREEN)
        content_frame.pack(fill='x', padx=10, pady=(20, 0))
        
        tk.Label(content_frame, text="Show:", 
                bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                font=Fonts.DIALOG_LABEL).pack(anchor='w')
        
        self.content_var = tk.StringVar(value="all")
        
        content_options = tk.Frame(content_frame, bg=Colors.LIGHT_GREEN)
        content_options.pack(fill='x', pady=(5, 0))
        
        tk.Radiobutton(content_options, text="All items", variable=self.content_var, value="all",
                      bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                      font=Fonts.DIALOG_LABEL,
                      selectcolor=Colors.LIGHT_GREEN).pack(side='left')
        
        tk.Radiobutton(content_options, text="Folders only", variable=self.content_var, value="folders",
                      bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                      font=Fonts.DIALOG_LABEL,
                      selectcolor=Colors.LIGHT_GREEN).pack(side='left', padx=(20, 0))
        
        tk.Radiobutton(content_options, text="Files only", variable=self.content_var, value="files",
                      bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                      font=Fonts.DIALOG_LABEL,
                      selectcolor=Colors.LIGHT_GREEN).pack(side='left', padx=(20, 0))
        
        # Buttons
        button_frame = tk.Frame(content, bg=Colors.LIGHT_GREEN)
        button_frame.pack(side='bottom', pady=20)
        
        scan_btn = tk.Button(button_frame, text="Scan", 
                            bg=Colors.DARK_GREEN, fg='white',
                            command=self.start_scan,
                            font=Fonts.DIALOG_BUTTON, relief='flat',
                            cursor='hand2', padx=20)
        scan_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              bg=Colors.INACTIVE_GRAY, fg='white',
                              command=self.cancel,
                              font=Fonts.DIALOG_BUTTON, relief='flat',
                              padx=20)
        cancel_btn.pack(side='left', padx=10)
    
    def auto_populate_folder(self):
        """Auto-populate the folder field with the best default folder"""
        try:
            best_folder = ExplorerDetector.get_best_default_folder()
            if best_folder:
                self.folder_var.set(best_folder)
                self.selected_folder = best_folder
        except Exception as e:
            print(f"Error auto-populating folder: {e}")
            try:
                fallback_folder = os.path.expanduser('~')
                self.folder_var.set(fallback_folder)
                self.selected_folder = fallback_folder
            except:
                pass
    
    def browse_folder(self):
        """Browse for folder to scan"""
        folder = filedialog.askdirectory(parent=self, title="Select Folder to Inventory")
        if folder:
            self.folder_var.set(folder)
            self.selected_folder = folder
    
    def start_scan(self):
        """Start the folder scan"""
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showwarning("Invalid Input", "Please select a folder to scan.")
            return
            
        if not os.path.exists(folder):
            messagebox.showerror("Invalid Folder", "The selected folder does not exist.")
            return
        
        # Show progress window
        self.progress_window = ProgressWindow(self, "Scanning...")
        self.progress_window.update()
        
        # Start scan in background thread
        self.cancel_scan = False
        self.scan_thread = threading.Thread(target=self.perform_scan, args=(folder,))
        self.scan_thread.start()
    
    def perform_scan(self, folder):
        """Perform the actual folder scan"""
        try:
            self.inventory_data = []
            max_depth = self.depth_var.get()
            content_type = self.content_var.get()
            
            # Scan folder recursively
            self._scan_folder(folder, 0, max_depth, content_type)
            
            # Close progress window
            if self.progress_window:
                self.progress_window.after(0, self.progress_window.destroy)
            
            # Open inventory window in main thread
            self.after(0, self.show_inventory_window, folder)
            
        except Exception as e:
            if self.progress_window:
                self.progress_window.after(0, self.progress_window.destroy)
            self.after(0, lambda: messagebox.showerror("Scan Error", f"Error scanning folder: {str(e)}"))
    
    def _scan_folder(self, folder_path, current_depth, max_depth, content_type):
        """Recursively scan folder"""
        if self.cancel_scan:
            return
            
        try:
            path = Path(folder_path)
            
            # Update progress
            if self.progress_window:
                self.progress_window.after(0, lambda: self.progress_window.update_message(f"Scanning: {path.name}"))
            
            # Scan items in current folder
            for item in path.iterdir():
                if self.cancel_scan:
                    return
                    
                try:
                    if item.is_dir():
                        if content_type in ['all', 'folders']:
                            # Add folder to inventory
                            self.inventory_data.append({
                                'name': item.name,
                                'path': str(item),
                                'type': 'Folder',
                                'size': self._get_folder_size(item),
                                'modified': datetime.fromtimestamp(item.stat().st_mtime)
                            })
                        
                        # Recursively scan subfolder if within depth limit
                        if max_depth == 0 or current_depth < max_depth:
                            self._scan_folder(item, current_depth + 1, max_depth, content_type)
                            
                    elif item.is_file() and content_type in ['all', 'files']:
                        # Add file to inventory
                        self.inventory_data.append({
                            'name': item.name,
                            'path': str(item),
                            'type': item.suffix[1:].upper() if item.suffix else 'File',
                            'size': item.stat().st_size,
                            'modified': datetime.fromtimestamp(item.stat().st_mtime)
                        })
                        
                except Exception as e:
                    print(f"Error scanning {item}: {e}")
                    
        except Exception as e:
            print(f"Error scanning folder {folder_path}: {e}")
    
    def _get_folder_size(self, folder):
        """Get folder item count"""
        try:
            count = len(list(folder.iterdir()))
            return count
        except:
            return 0
    
    def show_inventory_window(self, folder):
        """Show the inventory window with scan results"""
        # Close dialog
        self.destroy()
        
        # Create and show inventory window
        inventory_window = FolderInventoryWindow(self.master, folder, self.inventory_data)
        inventory_window.lift()
        inventory_window.focus_force()
    
    def cancel(self):
        """Cancel the dialog or scan"""
        self.cancel_scan = True
        if self.scan_thread and self.scan_thread.is_alive():
            # Wait briefly for thread to stop
            self.scan_thread.join(timeout=0.5)
        self.destroy()


class ProgressWindow(SimpleWindow):
    """Simple progress window for scanning"""
    
    def __init__(self, parent, title="Progress"):
        super().__init__(parent, title, resize_handles=None)
        
        self.geometry("300x120")
        
        # Center on parent
        self.update_idletasks()
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 120) // 2
        self.geometry(f"300x120+{x}+{y}")
        
        # Set background color
        self.content_frame.configure(bg=Colors.LIGHT_GREEN)
        
        # Create content
        self.message_label = tk.Label(self.content_frame, text="Scanning folders...",
                                     bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                                     font=Fonts.DIALOG_LABEL)
        self.message_label.pack(pady=20)
        
        # Progress indicator
        self.progress_label = tk.Label(self.content_frame, text="⏳",
                                      bg=Colors.LIGHT_GREEN, fg=Colors.DARK_GREEN,
                                      font=('Arial', 24))
        self.progress_label.pack()
        
        self.animate()
    
    def update_message(self, message):
        """Update progress message"""
        self.message_label.config(text=message[:40] + "..." if len(message) > 40 else message)
    
    def animate(self):
        """Simple animation"""
        current = self.progress_label.cget("text")
        self.progress_label.config(text="⌛" if current == "⏳" else "⏳")
        self.after(500, self.animate)


class FolderInventoryWindow(SimpleWindow):
    """Window for displaying folder inventory using SimpleWindow with filtering"""
    
    def __init__(self, parent, initial_path=None, scan_data=None):
        self.current_path = Path(initial_path) if initial_path else Path.home()
        self.scan_data = scan_data
        
        # Set window title
        window_title = f"Folder Inventory - {self.current_path.name}"
        
        # Initialize SimpleWindow
        super().__init__(parent, window_title, resize_handles=None)
        
        # Set window size
        self.geometry("1000x700")
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1000) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"1000x700+{x}+{y}")
        
        # Set background color
        self.content_frame.configure(bg=Colors.LIGHT_GREEN)
        
        # Prepare data
        if self.scan_data:
            self.inventory_data = self._prepare_scan_data()
        else:
            self.inventory_data = self._prepare_folder_data()
        
        # Create the inventory view directly in the content frame
        self._create_inventory_view()
    
    def _create_inventory_view(self):
        """Create the inventory view directly in the content frame"""
        # Header info
        info_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        path_label = tk.Label(info_frame, text=f"Path: {self.current_path}", 
                             bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                             font=Fonts.DIALOG_LABEL, anchor='w')
        path_label.pack(side=tk.LEFT)
        
        items_label = tk.Label(info_frame, text=f"Items: {len(self.inventory_data)}", 
                              bg=Colors.LIGHT_GREEN, fg=Colors.DARK_GREEN,
                              font=Fonts.DIALOG_LABEL, anchor='e')
        items_label.pack(side=tk.RIGHT)
        
        # Main treeview area
        tree_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create Treeview
        self.tree = ttk.Treeview(tree_frame, columns=('Type', 'Size', 'Modified'), 
                                show='tree headings')
        
        # Configure columns
        self.tree.column('#0', width=300, minwidth=200)
        self.tree.column('Type', width=100, minwidth=80)
        self.tree.column('Size', width=120, minwidth=100)
        self.tree.column('Modified', width=150, minwidth=120)
        
        # Configure headings with filtering
        self.tree.heading('#0', text='Name', anchor='w', command=lambda: self._show_filter('name'))
        self.tree.heading('Type', text='Type', anchor='w', command=lambda: self._show_filter('type'))
        self.tree.heading('Size', text='Size', anchor='e', command=lambda: self._show_filter('size_display'))
        self.tree.heading('Modified', text='Modified', anchor='w', command=lambda: self._show_filter('modified_display'))
        
        # Initialize filter state
        self.active_filters = {}
        self.original_data = self.inventory_data.copy()
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Style the treeview
        style = ttk.Style()
        style.configure('Treeview', background=Colors.LIGHT_GREEN, 
                       foreground=Colors.BLACK, fieldbackground='white')
        style.configure('Treeview.Heading', background=Colors.DARK_GREEN,
                       foreground='white', font=('Arial', 10, 'bold'))
        style.map('Treeview',
                 background=[('selected', Colors.MEDIUM_GREEN)],
                 foreground=[('selected', 'white')])
        
        # Populate the tree
        self._populate_tree()
        
        # Bind events
        self.tree.bind('<Double-1>', self._on_tree_double_click)
        self.tree.bind('<Button-3>', self._on_tree_right_click)
        
        # Add filter status bar
        self.filter_frame = tk.Frame(self.content_frame, bg=Colors.DARK_GREEN, height=25)
        self.filter_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        self.filter_frame.pack_propagate(False)
        
        self.filter_status = tk.Label(self.filter_frame, text="No filters applied", 
                                     bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                                     font=('Arial', 9))
        self.filter_status.pack(side=tk.LEFT, padx=5, pady=2)
        
        clear_filters_btn = tk.Button(self.filter_frame, text="Clear All Filters", 
                                     bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                                     command=self._clear_all_filters,
                                     font=('Arial', 9), relief=tk.RAISED, bd=1)
        clear_filters_btn.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def _populate_tree(self):
        """Populate the treeview with inventory data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add items to tree
        for item_data in self.inventory_data:
            self.tree.insert('', 'end', 
                           text=item_data['name'],
                           values=(item_data['type'], 
                                  item_data['size_display'],
                                  item_data['modified_display']),
                           tags=(item_data['path'],))
    
    def _on_tree_double_click(self, event):
        """Handle double-click on tree item"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        if not item['tags']:
            return
            
        path = Path(item['tags'][0])
        
        if path.is_dir():
            # Navigate to folder
            new_window = FolderInventoryWindow(self.master, str(path))
            self.close_window()
        else:
            # Open file
            try:
                os.startfile(str(path))
            except:
                messagebox.showerror("Error", f"Cannot open {path.name}")
    
    def _on_tree_right_click(self, event):
        """Handle right-click context menu"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.tree.selection_set(item)
            
            # Create context menu
            menu = tk.Menu(self, tearoff=0)
            menu.configure(bg=Colors.DARK_GREEN, fg='white',
                          activebackground=Colors.MEDIUM_GREEN,
                          activeforeground='white')
            
            # Get selected item info
            tree_item = self.tree.item(item)
            if tree_item['tags']:
                path = Path(tree_item['tags'][0])
                
                if path.is_file():
                    menu.add_command(label="Open", command=lambda: self._open_file(path))
                    menu.add_separator()
                    
                menu.add_command(label="Properties", command=lambda: self._show_properties(path))
                
                # Show menu
                menu.post(event.x_root, event.y_root)
    
    def _open_file(self, path):
        """Open file with default application"""
        try:
            os.startfile(str(path))
        except:
            messagebox.showerror("Error", f"Cannot open {path.name}")
    
    def _show_properties(self, path):
        """Show file/folder properties"""
        try:
            subprocess.run(['explorer', '/select,', str(path)])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot show properties: {str(e)}")
    
    def _prepare_scan_data(self):
        """Prepare scanned data"""
        inventory_data = []
        
        for item in self.scan_data:
            # Format size display
            if item['type'] == 'Folder':
                size_display = f"{item['size']} items"
            else:
                size_display = self._format_size(item['size'])
            
            # Format modified date
            modified_display = item['modified'].strftime('%Y-%m-%d %H:%M')
            
            inventory_data.append({
                'name': item['name'],
                'type': item['type'],
                'size': item['size'],
                'size_display': size_display,
                'modified': item['modified'],
                'modified_display': modified_display,
                'path': item['path']
            })
        
        return inventory_data
    
    def _prepare_folder_data(self):
        """Prepare folder data"""
        inventory_data = []
        
        try:
            path = self.current_path
            if not path.exists():
                return inventory_data
            
            # Add folders first
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    try:
                        item_count = len(list(item.iterdir()))
                        modified = datetime.fromtimestamp(item.stat().st_mtime)
                        inventory_data.append({
                            'name': item.name,
                            'type': 'Folder',
                            'size': item_count,
                            'size_display': f"{item_count} items",
                            'modified': modified,
                            'modified_display': modified.strftime('%Y-%m-%d %H:%M'),
                            'path': str(item)
                        })
                    except:
                        continue
            
            # Add files
            for item in sorted(path.iterdir()):
                if item.is_file():
                    try:
                        file_size = item.stat().st_size
                        modified = datetime.fromtimestamp(item.stat().st_mtime)
                        file_type = item.suffix[1:].upper() if item.suffix else 'File'
                        
                        inventory_data.append({
                            'name': item.name,
                            'type': file_type,
                            'size': file_size,
                            'size_display': self._format_size(file_size),
                            'modified': modified,
                            'modified_display': modified.strftime('%Y-%m-%d %H:%M'),
                            'path': str(item)
                        })
                    except:
                        continue
            
        except Exception as e:
            print(f"Error preparing folder data: {e}")
        
        return inventory_data
    
    def _format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _show_filter(self, column_key):
        """Show filter dialog for a column"""
        # Get unique values for this column
        unique_values = set()
        for item in self.original_data:
            value = str(item.get(column_key, ''))
            if value:
                unique_values.add(value)
        
        unique_values = sorted(list(unique_values))
        
        # Get current selection
        current_selection = self.active_filters.get(column_key, set())
        
        # Show filter dialog
        from ...ui.window_base import FilterMenuDialog
        
        column_headers = {
            'name': 'Name',
            'type': 'Type', 
            'size_display': 'Size',
            'modified_display': 'Modified'
        }
        
        header = column_headers.get(column_key, column_key)
        FilterMenuDialog(self, column_key, header, unique_values, 
                        current_selection, self._apply_filter)
    
    def _apply_filter(self, column_key, selected_values):
        """Apply filter to column"""
        if selected_values:
            self.active_filters[column_key] = set(selected_values)
        else:
            self.active_filters.pop(column_key, None)
        
        self._filter_data()
        self._update_filter_status()
        self._update_column_headers()
    
    def _filter_data(self):
        """Apply all active filters to data"""
        self.inventory_data = []
        
        for item in self.original_data:
            include_item = True
            
            for filter_col, filter_values in self.active_filters.items():
                item_value = str(item.get(filter_col, ''))
                if item_value not in filter_values:
                    include_item = False
                    break
            
            if include_item:
                self.inventory_data.append(item)
        
        self._populate_tree()
        
        # Update items count
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and "Items:" in child.cget("text"):
                        child.config(text=f"Items: {len(self.inventory_data)}")
                        break
                break
    
    def _update_filter_status(self):
        """Update filter status display"""
        if not self.active_filters:
            self.filter_status.config(text="No filters applied")
        else:
            filter_count = len(self.active_filters)
            self.filter_status.config(text=f"{filter_count} filter{'s' if filter_count > 1 else ''} applied")
    
    def _update_column_headers(self):
        """Update column headers to show filter indicators"""
        headers = {
            'name': 'Name',
            'type': 'Type',
            'size_display': 'Size', 
            'modified_display': 'Modified'
        }
        
        for col_key, header_text in headers.items():
            if col_key in self.active_filters:
                display_text = f"{header_text} ▼"
            else:
                display_text = header_text
                
            if col_key == 'name':
                self.tree.heading('#0', text=display_text)
            elif col_key == 'type':
                self.tree.heading('Type', text=display_text)
            elif col_key == 'size_display':
                self.tree.heading('Size', text=display_text)
            elif col_key == 'modified_display':
                self.tree.heading('Modified', text=display_text)
    
    def _clear_all_filters(self):
        """Clear all active filters"""
        self.active_filters = {}
        self.inventory_data = self.original_data.copy()
        self._populate_tree()
        self._update_filter_status()
        self._update_column_headers()
        
        # Update items count
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and "Items:" in child.cget("text"):
                        child.config(text=f"Items: {len(self.inventory_data)}")
                        break
                break