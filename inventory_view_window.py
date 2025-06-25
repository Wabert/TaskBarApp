# inventory_view_window.py
"""
Interactive inventory view window with Excel-like filtering capabilities
This component will be reused throughout the SuiteView project for data grids
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import Colors, Fonts, Dimensions
from ui_components import CustomDialog

class InventoryViewWindow(tk.Toplevel):
    """Interactive window for viewing inventory data with Excel-like filtering"""
    
    def __init__(self, parent, inventory_data, error_data, scan_info):
        super().__init__(parent)
        self.parent = parent
        self.inventory_data = inventory_data.copy()  # Original data
        self.filtered_data = inventory_data.copy()   # Current filtered data
        self.error_data = error_data
        self.scan_info = scan_info
        
        # Filter state tracking
        self.active_filters = {}  # column_name -> set of selected values
        self.column_unique_values = {}  # column_name -> list of unique values
        
        # Window setup
        self.title("Folder Inventory - Interactive View")
        self.configure(bg=Colors.DARK_GREEN)
        self.attributes('-topmost', True)
        self.geometry("1000x700")
        
        # Make window resizable
        self.resizable(True, True)
        
        # Main container
        self.main_frame = tk.Frame(self, bg=Colors.DARK_GREEN, relief=tk.RAISED, bd=2)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create header with scan information
        self.create_header()
        
        # Create the filterable data grid
        self.create_data_grid()
        
        # Create footer with action buttons
        self.create_footer()
        
        # Initialize data
        self.populate_grid()
        self.update_stats()
        
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center the window
        self.center_window()
    
    def create_header(self):
        """Create header with scan information"""
        header_frame = tk.Frame(self.main_frame, bg=Colors.LIGHT_GREEN, relief=tk.RAISED, bd=1)
        header_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Title
        title_label = tk.Label(header_frame, text="📁 Folder Inventory Results", 
                              bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=5)
        
        # Scan information in a grid
        info_frame = tk.Frame(header_frame, bg=Colors.LIGHT_GREEN)
        info_frame.pack(pady=5)
        
        # Row 1: Folder and Date
        tk.Label(info_frame, text="Scanned Folder:", bg=Colors.LIGHT_GREEN, 
                fg=Colors.BLACK, font=Fonts.DIALOG_LABEL).grid(row=0, column=0, sticky='w', padx=5)
        tk.Label(info_frame, text=self.scan_info['folder'], bg=Colors.LIGHT_GREEN, 
                fg=Colors.DARK_GREEN, font=Fonts.DIALOG_LABEL).grid(row=0, column=1, sticky='w', padx=5)
        
        tk.Label(info_frame, text="Generated:", bg=Colors.LIGHT_GREEN, 
                fg=Colors.BLACK, font=Fonts.DIALOG_LABEL).grid(row=0, column=2, sticky='w', padx=20)
        tk.Label(info_frame, text=self.scan_info['generated'], bg=Colors.LIGHT_GREEN, 
                fg=Colors.DARK_GREEN, font=Fonts.DIALOG_LABEL).grid(row=0, column=3, sticky='w', padx=5)
        
        # Row 2: Total Items and Content Type
        self.stats_label = tk.Label(info_frame, text="", bg=Colors.LIGHT_GREEN, 
                                   fg=Colors.BLACK, font=Fonts.DIALOG_LABEL)
        self.stats_label.grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        content_type_text = {
            'files': 'Files Only',
            'folders': 'Folders Only', 
            'both': 'Files and Folders'
        }.get(self.scan_info['content_type'], 'Unknown')
        
        tk.Label(info_frame, text=f"Content: {content_type_text}", bg=Colors.LIGHT_GREEN, 
                fg=Colors.DARK_GREEN, font=Fonts.DIALOG_LABEL).grid(row=1, column=2, columnspan=2, sticky='w', padx=20)
    
    def create_data_grid(self):
        """Create the main data grid with filtering"""
        # Grid container
        grid_frame = tk.Frame(self.main_frame, bg=Colors.LIGHT_GREEN, relief=tk.SUNKEN, bd=1)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create Treeview for the data grid
        self.tree = ttk.Treeview(grid_frame, show='tree headings')
        
        # Define columns (excluding Size (Bytes) from display but keeping in data)
        self.columns = ['Name', 'Full Path', 'Type', 'Size', 'Modified Date']
        self.tree['columns'] = self.columns
        
        # Configure tree column (hidden)
        self.tree.column('#0', width=0, stretch=False)
        self.tree.heading('#0', text='')
        
        # Configure data columns
        column_widths = {
            'Name': 200,
            'Full Path': 300,
            'Type': 80,
            'Size': 100,
            'Modified Date': 150
        }
        
        for col in self.columns:
            self.tree.column(col, width=column_widths.get(col, 100), anchor='w')
            # Create clickable headers for filtering
            self.tree.heading(col, text=f"{col} ▼", command=lambda c=col: self.show_filter_menu(c))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(grid_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack grid components
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(0, weight=1)
        
        # Style the treeview
        style = ttk.Style()
        style.configure('Treeview', background=Colors.LIGHT_GREEN, 
                       foreground=Colors.BLACK, fieldbackground=Colors.LIGHT_GREEN)
        style.configure('Treeview.Heading', background=Colors.MEDIUM_GREEN,
                       foreground=Colors.BLACK, font=Fonts.MENU_HEADER)
    
    def create_footer(self):
        """Create footer with action buttons and filter status"""
        footer_frame = tk.Frame(self.main_frame, bg=Colors.DARK_GREEN, height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=2, pady=2)
        footer_frame.pack_propagate(False)
        
        # Left side - filter status
        filter_frame = tk.Frame(footer_frame, bg=Colors.DARK_GREEN)
        filter_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.filter_status_label = tk.Label(filter_frame, text="No filters applied", 
                                           bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                                           font=Fonts.MENU_ITEM)
        self.filter_status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Right side - action buttons
        button_frame = tk.Frame(footer_frame, bg=Colors.DARK_GREEN)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Clear Filters button
        clear_btn = tk.Button(button_frame, text="Clear All Filters", 
                             bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                             relief=tk.RAISED, bd=1, cursor='hand2',
                             font=Fonts.MENU_ITEM, padx=10,
                             command=self.clear_all_filters)
        clear_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Export to Excel button
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
    
    def populate_grid(self):
        """Populate the grid with current filtered data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add filtered data
        for item in self.filtered_data:
            values = [item[col] for col in self.columns]
            self.tree.insert('', 'end', values=values)
        
        # Calculate unique values for each column (from original data for proper filtering)
        self.calculate_unique_values()
    
    def calculate_unique_values(self):
        """Calculate unique values for each column from original data"""
        self.column_unique_values = {}
        for col in self.columns:
            unique_vals = set()
            for item in self.inventory_data:
                val = item.get(col, '')
                if val != '':  # Don't include empty values
                    unique_vals.add(str(val))
            self.column_unique_values[col] = sorted(list(unique_vals))
    
    def show_filter_menu(self, column):
        """Show filter menu for a specific column"""
        FilterMenuDialog(self, column, self.column_unique_values[column], 
                        self.active_filters.get(column, set()), self.apply_filter)
    
    def apply_filter(self, column, selected_values):
        """Apply filter to a specific column"""
        if selected_values:
            self.active_filters[column] = set(selected_values)
        else:
            # Remove filter if no values selected
            if column in self.active_filters:
                del self.active_filters[column]
        
        # Apply all filters
        self.filter_data()
        self.update_display()
        self.update_filter_status()
    
    def filter_data(self):
        """Apply all active filters to the data"""
        self.filtered_data = []
        
        for item in self.inventory_data:
            include_item = True
            
            # Check each active filter
            for filter_col, filter_values in self.active_filters.items():
                item_value = str(item.get(filter_col, ''))
                if item_value not in filter_values:
                    include_item = False
                    break
            
            if include_item:
                self.filtered_data.append(item)
    
    def update_display(self):
        """Update the grid display with filtered data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add filtered data
        for item in self.filtered_data:
            values = [item[col] for col in self.columns]
            self.tree.insert('', 'end', values=values)
        
        # Update stats
        self.update_stats()
    
    def update_stats(self):
        """Update the statistics display"""
        total_original = len(self.inventory_data)
        total_filtered = len(self.filtered_data)
        
        if total_filtered == total_original:
            stats_text = f"Total Items: {total_original:,}"
        else:
            stats_text = f"Showing: {total_filtered:,} of {total_original:,} items"
        
        self.stats_label.config(text=stats_text)
    
    def update_filter_status(self):
        """Update the filter status display"""
        if not self.active_filters:
            self.filter_status_label.config(text="No filters applied")
        else:
            filter_count = len(self.active_filters)
            filter_text = f"{filter_count} filter{'s' if filter_count > 1 else ''} applied: "
            filter_details = []
            for col, values in self.active_filters.items():
                if len(values) == 1:
                    filter_details.append(f"{col}={list(values)[0]}")
                else:
                    filter_details.append(f"{col}({len(values)} values)")
            filter_text += ", ".join(filter_details)
            
            # Truncate if too long
            if len(filter_text) > 80:
                filter_text = filter_text[:77] + "..."
            
            self.filter_status_label.config(text=filter_text)
    
    def clear_all_filters(self):
        """Clear all active filters"""
        self.active_filters = {}
        self.filtered_data = self.inventory_data.copy()
        self.update_display()
        self.update_filter_status()
        
        # Update column headers to remove filter indicators
        for col in self.columns:
            self.tree.heading(col, text=f"{col} ▼")
    
    def export_to_excel(self):
        """Export the current filtered data to Excel"""
        from folder_inventory import ExcelInventoryCreator
        
        try:
            excel_creator = ExcelInventoryCreator()
            excel_creator.create_workbook(self.filtered_data, self.error_data, self.scan_info['folder'])
            messagebox.showinfo("Export Complete", "Filtered data has been exported to Excel.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to Excel:\n{str(e)}")
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_closing(self):
        """Handle window closing"""
        self.destroy()


class FilterMenuDialog(CustomDialog):
    """Dialog for selecting filter values for a column (Excel-like)"""
    
    def __init__(self, parent, column_name, unique_values, current_selection, apply_callback):
        super().__init__(parent, f"Filter: {column_name}", width=350, height=400)
        
        self.column_name = column_name
        self.unique_values = unique_values
        self.current_selection = current_selection.copy()
        self.apply_callback = apply_callback
        
        # If no current selection, default to all selected
        if not self.current_selection:
            self.current_selection = set(unique_values)
        
        self.create_filter_interface()
        self.create_action_buttons()
    
    def create_filter_interface(self):
        """Create the filter selection interface"""
        # Search box
        search_frame = tk.Frame(self.dialog_content, bg=Colors.LIGHT_GREEN)
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text="Search:", bg=Colors.LIGHT_GREEN, 
                fg=Colors.BLACK, font=Fonts.DIALOG_LABEL).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_list)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=Fonts.DIALOG_LABEL)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Select All / None buttons
        select_frame = tk.Frame(self.dialog_content, bg=Colors.LIGHT_GREEN)
        select_frame.pack(fill=tk.X, pady=5)
        
        select_all_btn = tk.Button(select_frame, text="Select All", 
                                  bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                                  command=self.select_all, font=Fonts.DIALOG_LABEL)
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        select_none_btn = tk.Button(select_frame, text="Select None", 
                                   bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                                   command=self.select_none, font=Fonts.DIALOG_LABEL)
        select_none_btn.pack(side=tk.LEFT, padx=5)
        
        # Listbox with checkboxes (simulated with Treeview)
        list_frame = tk.Frame(self.dialog_content, bg=Colors.LIGHT_GREEN)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create Treeview for checkbox list
        self.filter_tree = ttk.Treeview(list_frame, show='tree', height=12)
        self.filter_tree.column('#0', width=300)
        
        # Scrollbar for the list
        filter_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                        command=self.filter_tree.yview)
        self.filter_tree.configure(yscrollcommand=filter_scrollbar.set)
        
        self.filter_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        filter_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate the list
        self.populate_filter_list()
        
        # Bind double-click to toggle selection
        self.filter_tree.bind('<Double-1>', self.toggle_item)
        self.filter_tree.bind('<Return>', self.toggle_item)
    
    def populate_filter_list(self, search_text=""):
        """Populate the filter list with checkboxes"""
        # Clear existing items
        for item in self.filter_tree.get_children():
            self.filter_tree.delete(item)
        
        # Filter values based on search
        filtered_values = [val for val in self.unique_values 
                          if search_text.lower() in val.lower()] if search_text else self.unique_values
        
        # Add items with checkbox indicators
        for value in filtered_values:
            checkbox = "☑" if value in self.current_selection else "☐"
            display_text = f"{checkbox} {value}"
            item_id = self.filter_tree.insert('', 'end', text=display_text, values=[value])
    
    def filter_list(self, *args):
        """Filter the list based on search text"""
        search_text = self.search_var.get()
        self.populate_filter_list(search_text)
    
    def toggle_item(self, event=None):
        """Toggle selection of an item"""
        selected_item = self.filter_tree.selection()
        if not selected_item:
            return
        
        item_id = selected_item[0]
        values = self.filter_tree.item(item_id, 'values')
        if values:
            value = values[0]
            
            if value in self.current_selection:
                self.current_selection.remove(value)
            else:
                self.current_selection.add(value)
            
            # Update display
            search_text = self.search_var.get()
            self.populate_filter_list(search_text)
    
    def select_all(self):
        """Select all visible items"""
        search_text = self.search_var.get()
        filtered_values = [val for val in self.unique_values 
                          if search_text.lower() in val.lower()] if search_text else self.unique_values
        
        for value in filtered_values:
            self.current_selection.add(value)
        
        self.populate_filter_list(search_text)
    
    def select_none(self):
        """Deselect all visible items"""
        search_text = self.search_var.get()
        filtered_values = [val for val in self.unique_values 
                          if search_text.lower() in val.lower()] if search_text else self.unique_values
        
        for value in filtered_values:
            self.current_selection.discard(value)
        
        self.populate_filter_list(search_text)
    
    def create_action_buttons(self):
        """Create OK and Cancel buttons"""
        button_container = tk.Frame(self.button_frame, bg=Colors.LIGHT_GREEN)
        button_container.pack(expand=True)
        
        ok_btn = tk.Button(button_container, text="OK", 
                          bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                          command=self.apply_filter, width=Dimensions.DIALOG_BUTTON_WIDTH,
                          font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        ok_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_container, text="Cancel", 
                              bg=Colors.INACTIVE_GRAY, fg=Colors.WHITE,
                              command=self.cancel, width=Dimensions.DIALOG_BUTTON_WIDTH,
                              font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        ok_btn.focus_set()
    
    def apply_filter(self):
        """Apply the selected filter"""
        self.apply_callback(self.column_name, list(self.current_selection))
        self.destroy()
    
    def cancel(self):
        """Cancel without applying changes"""
        self.destroy()