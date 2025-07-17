"""
FilterView component for SuiteView Taskbar Application
A reusable interactive frame for viewing tabular data with Excel-like filtering
"""
import tkinter as tk
from tkinter import ttk
from ..core.config import Colors, Fonts
from .dialogs import FilterMenuDialog
from typing import List, Dict, Any, Optional, Callable, Set


class FilterView(tk.Frame):
    """
    Reusable interactive frame for viewing any tabular data with Excel-like filtering
    Inherits from tk.Frame for embedding in other windows
    
    Args:
        parent: Parent frame/window to populate
        data: List of dictionaries containing the data to display
        columns: List of column configurations, each with:
            - key: Dictionary key for this column
            - header: Display name for column header
            - width: Column width (default: 100)
            - type: Data type ('text', 'number', 'date') for sorting (default: 'text')
        on_item_click: Callback function(item) when item is clicked
        on_item_double_click: Callback function(item) when item is double-clicked
    """
    
    def __init__(self, parent, data: List[Dict[str, Any]], columns: Optional[List[Dict[str, Any]]] = None, 
                 on_item_click: Optional[Callable] = None, 
                 on_item_double_click: Optional[Callable] = None):
        # Initialize Frame
        super().__init__(parent, bg=Colors.LIGHT_GREEN)
        
        # Store data
        self.original_data = data.copy() if data else []
        self.filtered_data = self.original_data.copy()
        
        # Configuration
        self.column_configs = columns or self._auto_generate_columns()
        self.on_item_click = on_item_click
        self.on_item_double_click = on_item_double_click
        
        # Extract column information
        self.columns = [col['key'] for col in self.column_configs]
        self.column_headers = {col['key']: col.get('header', col['key']) for col in self.column_configs}
        self.column_widths = {col['key']: col.get('width', 100) for col in self.column_configs}
        self.column_types = {col['key']: col.get('type', 'text') for col in self.column_configs}
        
        # Filter state tracking
        self.active_filters: Dict[str, Set[str]] = {}
        self.column_unique_values: Dict[str, List[str]] = {}
        
        # Create UI components
        self.create_data_grid()
        
        # Populate
        self.populate_grid()
        
        # Expose the tree object
        self.tree = self.data_tree
        
    def _auto_generate_columns(self) -> List[Dict[str, Any]]:
        """Auto-generate column configuration from data"""
        if not self.original_data:
            return []
        
        # Get all unique keys from data
        all_keys = set()
        for item in self.original_data:
            all_keys.update(item.keys())
        
        # Create column config for each key
        columns = []
        for key in sorted(all_keys):
            columns.append({
                'key': key,
                'header': key.replace('_', ' ').title(),
                'width': 150,
                'type': self._guess_column_type(key)
            })
        
        return columns
    
    def _guess_column_type(self, key: str) -> str:
        """Guess column type based on key name and sample data"""
        key_lower = key.lower()
        
        # Check key name patterns
        if any(word in key_lower for word in ['date', 'time', 'created', 'modified', 'updated']):
            return 'date'
        elif any(word in key_lower for word in ['count', 'number', 'size', 'bytes', 'id', 'qty', 'quantity']):
            return 'number'
        
        # Check sample data
        sample_values = []
        for item in self.original_data[:10]:  # Check first 10 items
            if key in item and item[key] is not None:
                sample_values.append(item[key])
        
        if sample_values:
            # Check if all values are numeric
            try:
                for val in sample_values:
                    float(str(val).replace(',', ''))
                return 'number'
            except:
                pass
        
        return 'text'
    
    def create_data_grid(self):
        """Create the main data grid with filtering"""
        grid_frame = tk.Frame(self, bg=Colors.LIGHT_GREEN, relief=tk.SUNKEN, bd=1)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Create Treeview
        self.data_tree = ttk.Treeview(grid_frame, show='tree headings')
        self.data_tree['columns'] = self.columns
        
        # Configure columns
        self.data_tree.column('#0', width=0, stretch=False)
        self.data_tree.heading('#0', text='')
        
        for col in self.columns:
            self.data_tree.column(col, width=self.column_widths.get(col, 100), anchor='w')
            header_text = self.column_headers.get(col, col)
            self.data_tree.heading(col, text=header_text, command=lambda c=col: self.show_filter_menu(c))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        h_scrollbar = ttk.Scrollbar(grid_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack components
        self.data_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(0, weight=1)
        
        # Style
        style = ttk.Style()
        style.configure('Treeview', background=Colors.LIGHT_GREEN, 
                       foreground=Colors.BLACK, fieldbackground=Colors.LIGHT_GREEN)
        style.configure('Treeview.Heading', background=Colors.MEDIUM_GREEN,
                       foreground=Colors.WHITE, font=Fonts.MENU_HEADER)
        
        # Bind click events
        if self.on_item_click:
            self.data_tree.bind('<ButtonRelease-1>', self._handle_item_click)
        if self.on_item_double_click:
            self.data_tree.bind('<Double-Button-1>', self._handle_item_double_click)
    
    def _handle_item_click(self, event):
        """Handle single click on item with column detection"""
        selection = self.data_tree.selection()
        if selection and self.on_item_click:
            item_id = selection[0]
            item_index = self.data_tree.index(item_id)
            
            if 0 <= item_index < len(self.filtered_data):
                # Determine which column was clicked
                column_id = self.data_tree.identify_column(event.x)
                
                # Convert column id (#1, #2, etc.) to column index
                if column_id:
                    try:
                        col_index = int(column_id.replace('#', '')) - 1
                        if 0 <= col_index < len(self.columns):
                            column_key = self.columns[col_index]
                            # Pass both item and column to callback
                            if hasattr(self.on_item_click, '__code__') and self.on_item_click.__code__.co_argcount > 2:
                                # New style callback with column info
                                self.on_item_click(self.filtered_data[item_index], column_key)
                            else:
                                # Old style callback without column info
                                self.on_item_click(self.filtered_data[item_index])
                    except:
                        # Fallback to just item
                        self.on_item_click(self.filtered_data[item_index])
    
    def _handle_item_double_click(self, event):
        """Handle double click on item"""
        selection = self.data_tree.selection()
        if selection and self.on_item_double_click:
            item_id = selection[0]
            item_index = self.data_tree.index(item_id)
            if 0 <= item_index < len(self.filtered_data):
                self.on_item_double_click(self.filtered_data[item_index])
    
    def populate_grid(self):
        """Populate the grid with current filtered data"""
        # Clear existing items
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Add filtered data
        for item in self.filtered_data:
            values = []
            for col in self.columns:
                value = item.get(col, '')
                # Format based on type
                if self.column_types.get(col) == 'number' and value != '':
                    try:
                        # Format numbers with commas
                        if isinstance(value, (int, float)):
                            value = f"{value:,}"
                    except:
                        pass
                values.append(str(value))
            
            self.data_tree.insert('', 'end', values=values)
        
        # Calculate unique values
        self.calculate_unique_values()
    
    def calculate_unique_values(self):
        """Calculate unique values for each column from filtered data"""
        self.column_unique_values = {}
        
        for col in self.columns:
            unique_vals = set()
            for item in self.filtered_data:
                val = item.get(col, '')
                if val != '':
                    unique_vals.add(str(val))
            self.column_unique_values[col] = sorted(list(unique_vals))
    
    def show_filter_menu(self, column: str):
        """Show filter menu for a specific column"""
        available_values = self.get_available_values_for_column(column)
        # Create filter dialog - need to find a suitable parent window
        parent_window = self.winfo_toplevel()
        
        class FilterDialog(FilterMenuDialog):
            """Custom filter dialog that calls our apply_filter method"""
            def __init__(self, parent, column, column_header, available_values, current_filter, apply_callback):
                self.column = column
                self.apply_callback = apply_callback
                self.available_values = available_values
                self.current_filter = current_filter
                
                # Create the dialog with basic title
                super().__init__(parent, f"Filter: {column_header}")
                
            def create_widgets(self):
                """Create filter widgets"""
                # Header
                header = tk.Label(self.content_frame, text=f"Select values to show:",
                                bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                                font=Fonts.DIALOG_HEADER)
                header.pack(pady=(10, 20))
                
                # Values list with checkboxes
                values_frame = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY)
                values_frame.pack(fill="both", expand=True, padx=20)
                
                # Scrollable frame for values
                canvas = tk.Canvas(values_frame, bg=Colors.BG_PRIMARY,
                                 highlightthickness=0, height=300)
                scrollbar = tk.Scrollbar(values_frame, orient="vertical",
                                       command=canvas.yview)
                inner_frame = tk.Frame(canvas, bg=Colors.BG_PRIMARY)
                
                canvas.configure(yscrollcommand=scrollbar.set)
                canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
                
                canvas.pack(side=tk.LEFT, fill="both", expand=True)
                scrollbar.pack(side=tk.RIGHT, fill="y")
                
                # Create checkboxes
                self.value_vars = {}
                for value in self.available_values:
                    var = tk.BooleanVar(value=value in self.current_filter)
                    self.value_vars[value] = var
                    
                    cb = tk.Checkbutton(inner_frame, text=value, variable=var,
                                      bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                                      selectcolor=Colors.BG_SECONDARY,
                                      activebackground=Colors.BG_PRIMARY,
                                      font=Fonts.MENU_ITEM)
                    cb.pack(anchor="w", pady=2, padx=10)
                
                # Update scroll region
                inner_frame.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox("all"))
                
                # Buttons
                button_frame = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY)
                button_frame.pack(side=tk.BOTTOM, fill="x", pady=10)
                
                apply_btn = tk.Button(button_frame, text="Apply",
                                    bg=Colors.PRIMARY_GREEN, fg=Colors.TEXT_WHITE,
                                    font=Fonts.BUTTON_SMALL, width=10,
                                    command=self.apply_filter)
                apply_btn.pack(side=tk.RIGHT, padx=5)
                
                clear_btn = tk.Button(button_frame, text="Clear",
                                    bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY,
                                    font=Fonts.BUTTON_SMALL, width=10,
                                    command=self.clear_filter)
                clear_btn.pack(side=tk.RIGHT, padx=5)
                
                cancel_btn = tk.Button(button_frame, text="Cancel",
                                     bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY,
                                     font=Fonts.BUTTON_SMALL, width=10,
                                     command=self.close)
                cancel_btn.pack(side=tk.RIGHT, padx=5)
            
            def apply_filter(self):
                """Apply the selected filter values"""
                selected_values = [val for val, var in self.value_vars.items() if var.get()]
                self.apply_callback(self.column, selected_values)
                self.close()
            
            def clear_filter(self):
                """Clear filter for this column"""
                self.apply_callback(self.column, [])
                self.close()
        
        # Create and show the filter dialog
        FilterDialog(parent_window, column, self.column_headers.get(column, column),
                    available_values, self.active_filters.get(column, set()), 
                    self.apply_filter)
    
    def get_available_values_for_column(self, column: str) -> List[str]:
        """Get all possible values for a column considering OTHER column filters"""
        available_values = set()
        
        temp_filters = self.active_filters.copy()
        if column in temp_filters:
            del temp_filters[column]
        
        for item in self.original_data:
            include_item = True
            
            for filter_col, filter_values in temp_filters.items():
                item_value = str(item.get(filter_col, ''))
                if item_value not in filter_values:
                    include_item = False
                    break
            
            if include_item:
                val = item.get(column, '')
                if val != '':
                    available_values.add(str(val))
        
        return sorted(list(available_values))
    
    def apply_filter(self, column: str, selected_values: List[str]):
        """Apply filter to a specific column"""
        if selected_values:
            self.active_filters[column] = set(selected_values)
        else:
            if column in self.active_filters:
                del self.active_filters[column]
        
        self.filter_data()
        self.update_display()
        self.update_column_headers()
    
    def filter_data(self):
        """Apply all active filters to the data"""
        self.filtered_data = []
        
        for item in self.original_data:
            include_item = True
            
            for filter_col, filter_values in self.active_filters.items():
                item_value = str(item.get(filter_col, ''))
                if item_value not in filter_values:
                    include_item = False
                    break
            
            if include_item:
                self.filtered_data.append(item)
    
    def update_display(self):
        """Update the grid display with filtered data"""
        self.populate_grid()

    def update_column_headers(self):
        """Update column headers to show filter indicators"""
        for col in self.columns:
            header_text = self.column_headers.get(col, col)
            if col in self.active_filters:
                self.data_tree.heading(col, text=f"{header_text} ▼")
            else:
                self.data_tree.heading(col, text=header_text)
    
    def clear_all_filters(self):
        """Clear all active filters"""
        self.active_filters = {}
        self.filtered_data = self.original_data.copy()
        self.update_display()
        self.update_column_headers()
    
    def refresh_data(self, new_data: List[Dict[str, Any]]):
        """Refresh the view with new data"""
        self.original_data = new_data.copy() if new_data else []
        self.filtered_data = self.original_data.copy()
        self.clear_all_filters()
        self.populate_grid()
    
    def get_selected_items(self) -> List[Dict[str, Any]]:
        """Get currently selected items"""
        selection = self.data_tree.selection()
        selected_items = []
        for item_id in selection:
            item_index = self.data_tree.index(item_id)
            if 0 <= item_index < len(self.filtered_data):
                selected_items.append(self.filtered_data[item_index])
        return selected_items
    
    def get_filtered_data(self) -> List[Dict[str, Any]]:
        """Get the currently filtered data"""
        return self.filtered_data.copy()