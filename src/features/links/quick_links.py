# quick_links.py
"""
Quick Links feature for SuiteView Taskbar
Contains the links menu, dialogs, and management interface
"""

import tkinter as tk
from tkinter import ttk, filedialog
from ...core.config import Colors, Fonts, Dimensions
from ...utils.utils import UIUtils, FileUtils
from ...ui.ui_components import CustomDialog, ConfirmationDialog, FormField, CategoryHeader, WarningDialog, ErrorDialog
from links_manager import LinksManager

class QuickLinksMenu(tk.Toplevel):
    """Enhanced right-click context menu for managing links with column layout"""
    
    def __init__(self, parent, taskbar_instance, x, y):
        super().__init__(parent)
        self.parent = parent
        self.taskbar_instance = taskbar_instance
        self.links_manager = taskbar_instance.links_manager
        
        # Window setup
        self.overrideredirect(True)
        self.configure(bg=Colors.DARK_GREEN)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.98)
        
        # Initialize resize variables
        self.is_resizing = False
        self.resize_start_y = 0
        self.original_height = 0
        self.bottom_y = 0  # Track bottom position for locked resizing
        
        # Initialize drag and drop variables
        self.is_dragging_link = False
        self.drag_start_time = 0
        self.drag_threshold = 5  # pixels to move before considering it a drag
        self.drag_time_threshold = 200  # milliseconds to wait before drag
        self.dragged_link_data = None
        self.dragged_link_index = None
        self.drag_visual = None
        self.drop_indicators = []
        
        # Position the menu
        self.geometry(f"+{x}+{y}")
        
        # Main container with dark green border
        self.main_frame = tk.Frame(self, bg=Colors.DARK_GREEN, relief=tk.RAISED, bd=2)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Header frame with buttons
        self.create_header()
        
        # Content area with light green background
        self.content_frame = tk.Frame(self.main_frame, bg=Colors.LIGHT_GREEN, relief=tk.SUNKEN, bd=1)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create column layout for all categories
        self.create_column_layout()
        
        # Bind events
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.focus_set()
        
        # Set minimum size based on content and stored preferences
        self.update_idletasks()
        self.menu_width = max(Dimensions.MENU_MIN_WIDTH, self.winfo_reqwidth())
        
        # Use stored menu height or default
        stored_height = self.links_manager.get_menu_height()
        calculated_height = max(Dimensions.MENU_MIN_HEIGHT, self.winfo_reqheight())
        self.menu_height = max(stored_height, calculated_height)
        
        self.geometry(f"{self.menu_width}x{self.menu_height}")
        
        # Store bottom position for locked resizing
        self.update_idletasks()
        self.bottom_y = self.winfo_y() + self.winfo_height()
        
        # Setup resize functionality
        self.setup_resize_functionality()
        
    
    def create_header(self):
        """Create header with title and buttons"""
        self.header_frame = tk.Frame(self.main_frame, bg=Colors.DARK_GREEN, height=25)
        self.header_frame.pack(fill=tk.X, padx=1, pady=1)
        self.header_frame.pack_propagate(False)
        
        # Create a resize area at the top of the header
        resize_area = tk.Frame(self.header_frame, bg=Colors.MEDIUM_GREEN, height=3, cursor='sb_v_double_arrow')
        resize_area.pack(fill=tk.X, side=tk.TOP)
        
        # Main header content
        header_content = tk.Frame(self.header_frame, bg=Colors.DARK_GREEN)
        header_content.pack(fill=tk.BOTH, expand=True)
        
        # Resize handle (left side) - more prominent
        resize_handle = tk.Label(header_content, text="═══", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                               font=('Arial', 6), cursor='sb_v_double_arrow', width=4)
        resize_handle.pack(side=tk.LEFT, padx=2, pady=3)
        
        # Title with resize capability
        title_label = tk.Label(header_content, text="Quick Links ↕", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                             font=Fonts.MENU_HEADER, cursor='sb_v_double_arrow')
        title_label.pack(side=tk.LEFT, padx=5, pady=3)
        
        # Bind resize events to multiple elements for better usability
        for widget in [resize_area, resize_handle, title_label, self.header_frame]:
            widget.bind("<Button-1>", self.start_resize)
            widget.bind("<B1-Motion>", self.do_resize)
            widget.bind("<ButtonRelease-1>", self.end_resize)
            widget.bind("<Enter>", lambda e: self.configure(cursor='sb_v_double_arrow'))
            widget.bind("<Leave>", lambda e: self.configure(cursor=''))
        
        # Buttons with green theme
        button_frame = tk.Frame(header_content, bg=Colors.DARK_GREEN)
        button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Add button
        add_btn = tk.Button(button_frame, text="Add", bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                           relief=tk.RAISED, bd=1, cursor='hand2', 
                           font=Fonts.MENU_ITEM, width=4, height=1,
                           command=self.add_new_link)
        add_btn.pack(side=tk.LEFT, padx=1)
        
        # # View button (placeholder for future features)
        # view_btn = tk.Button(button_frame, text="Vie", bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
        #                     relief=tk.RAISED, bd=1, cursor='hand2',
        #                     font=Fonts.MENU_ITEM, width=4, height=1)
        # view_btn.pack(side=tk.LEFT, padx=1)
        
        # Close button
        close_btn = tk.Button(button_frame, text="X", bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                             relief=tk.RAISED, bd=1, cursor='hand2',
                             font=Fonts.MENU_ITEM, width=3, height=1,
                             command=self.destroy)
        close_btn.pack(side=tk.LEFT, padx=1)
    
    def create_column_layout(self):
        """Create column layout showing all categories"""
        # Container for columns
        columns_frame = tk.Frame(self.content_frame, bg=Colors.LIGHT_GREEN)
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        categories = self.links_manager.get_categories()
        num_categories = len(categories)
        
        # Create columns for each category
        for i, category in enumerate(categories):
            column_frame = tk.Frame(columns_frame, bg=Colors.LIGHT_GREEN, relief=tk.FLAT)
            column_frame.grid(row=0, column=i, sticky='nsew', padx=2, pady=1)
            
            # Configure grid weights for equal distribution
            columns_frame.grid_columnconfigure(i, weight=1)
        
        columns_frame.grid_rowconfigure(0, weight=1)
        
        # Populate each column
        for i, category in enumerate(categories):
            self.create_category_column(columns_frame, category, i)
    
    def create_category_column(self, parent, category, column_index):
        """Create a column for a specific category"""
        # Get the column frame
        column_frame = parent.grid_slaves(row=0, column=column_index)[0]
        
        # Category header
        header = CategoryHeader(column_frame, category)
        header.pack(fill=tk.X, pady=(0, 2))
        
        # Links container with light green background
        links_container = tk.Frame(column_frame, bg=Colors.LIGHT_GREEN)
        links_container.pack(fill=tk.BOTH, expand=True)
        
        # Store category for drop operations
        links_container.category = category
        links_container.bind("<Enter>", lambda e: self.on_category_drop_zone_enter(e, category))
        links_container.bind("<Leave>", lambda e: self.on_category_drop_zone_leave(e, category))
        
        # Get links for this category
        links = self.links_manager.get_links_by_category(category)
        
        if links:
            for link in links:
                # Find the actual index in the full links list
                actual_index = self.links_manager.get_all_links().index(link)
                self.create_compact_link_item(links_container, link, actual_index)
        else:
            # Empty state - also acts as a drop zone
            empty_label = tk.Label(links_container, text="", bg=Colors.LIGHT_GREEN, fg=Colors.DARK_GREEN,
                                 font=(Fonts.MENU_ITEM[0], Fonts.MENU_ITEM[1], 'italic'))
            empty_label.pack(pady=5)
            empty_label.category = category
            empty_label.bind("<Enter>", lambda e: self.on_empty_category_enter(e, category))
            empty_label.bind("<Leave>", lambda e: self.on_empty_category_leave(e, category))
    
    def create_compact_link_item(self, parent, link, index):
        """Create a compact link item with drag-and-drop support"""
        # Create a frame to hold the link (easier for drag operations)
        link_frame = tk.Frame(parent, bg=Colors.LIGHT_GREEN, relief=tk.FLAT)
        link_frame.pack(fill=tk.X, padx=2, pady=1)
        
        # Create the link label
        link_label = tk.Label(link_frame, text=f"{link['name']}", bg=Colors.LIGHT_GREEN, fg=Colors.BLACK,
                             font=Fonts.MENU_ITEM, anchor='w', height=1,
                             cursor='hand2', relief=tk.FLAT, padx=5, pady=2)
        link_label.pack(fill=tk.X)
        
        # Store link data for drag operations
        link_frame.link_data = link
        link_frame.link_index = index
        link_frame.category = link['category']
        link_label.link_data = link
        link_label.link_index = index
        link_label.category = link['category']
        
        # Apply hover effects
        UIUtils.apply_hover_effect(link_label, Colors.LIGHT_GREEN, Colors.HOVER_GREEN, 
                                  Colors.BLACK, Colors.WHITE)
        
        # Bind drag and drop events
        for widget in [link_frame, link_label]:
            widget.bind("<Button-1>", lambda e, l=link, i=index: self.on_link_press(e, l, i))
            widget.bind("<B1-Motion>", lambda e, l=link, i=index: self.on_link_drag(e, l, i))
            widget.bind("<ButtonRelease-1>", lambda e, l=link, i=index: self.on_link_release(e, l, i))
            widget.bind("<Button-3>", lambda e, l=link, i=index: self.show_link_context_menu(e, l, i))
        
        # Mark as drop zone
        link_frame.bind("<Enter>", lambda e: self.on_drop_zone_enter(e, link, index))
        link_frame.bind("<Leave>", lambda e: self.on_drop_zone_leave(e, link, index))
    
    def show_link_context_menu(self, event, link, index):
        """Show context menu for individual link"""
        context_menu = tk.Menu(self, tearoff=0, bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                              activebackground=Colors.HOVER_GREEN, activeforeground=Colors.WHITE)
        
        context_menu.add_command(label=f"Open {link['name']}", 
                                command=lambda: FileUtils.open_path(link['path'], self.parent))
        context_menu.add_separator()
        context_menu.add_command(label="Edit", 
                                command=lambda: self.edit_link(link, index))
        context_menu.add_command(label="Delete", 
                                command=lambda: self.delete_link(link, index))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def edit_link(self, link, index):
        """Edit an existing link"""
        self.destroy()
        AddEditLinkDialog.show_edit_dialog(self.parent, self.links_manager, self.taskbar_instance, link, index)
    
    def delete_link(self, link, index):
        """Delete a link with confirmation"""
        result = ConfirmationDialog.ask(
            self.parent, 
            "Delete Link", 
            f"Are you sure you want to delete:\n'{link['name']}'?"
        )
        
        if result:
            self.links_manager.remove_link(index)
            self.destroy()
            # Refresh menu
            self.taskbar_instance.show_links_menu(None)
    
    def add_new_link(self):
        """Show dialog to add a new link"""
        self.destroy()
        AddEditLinkDialog.show_add_dialog(self.parent, self.links_manager, self.taskbar_instance)
    
    def setup_resize_functionality(self):
        """Setup resize functionality with minimum size constraints"""
        self.min_height = 150  # Minimum height
        self.max_height = 600  # Maximum height for usability
        
        # Allow window to be resizable
        self.resizable(False, True)  # Only allow vertical resizing
    
    def start_resize(self, event):
        """Start resizing operation"""
        self.is_resizing = True
        self.resize_start_y = event.y_root
        self.original_height = self.winfo_height()
        self.original_x = self.winfo_x()
        
        # Update bottom position
        self.bottom_y = self.winfo_y() + self.winfo_height()
        
        # Change cursor to indicate resizing
        self.configure(cursor='sb_v_double_arrow')
        
        # Visual feedback
        self.header_frame.configure(bg=Colors.HOVER_GREEN)
        
        print(f"Starting resize: height={self.original_height}, bottom_y={self.bottom_y}")
    
    def do_resize(self, event):
        """Handle resize drag motion"""
        if not self.is_resizing:
            return
        
        # Calculate the change in Y position
        delta_y = event.y_root - self.resize_start_y
        
        # Calculate new height (drag up = smaller delta = taller window)
        new_height = self.original_height - delta_y
        
        # Apply constraints
        new_height = max(self.min_height, min(self.max_height, new_height))
        
        # Calculate new Y position to keep bottom locked
        new_y = self.bottom_y - new_height
        
        # Apply the new geometry
        try:
            self.geometry(f"{self.menu_width}x{int(new_height)}+{self.original_x}+{int(new_y)}")
        except Exception as e:
            print(f"Resize error: {e}")
    
    def end_resize(self, event):
        """End resizing operation"""
        self.is_resizing = False
        self.configure(cursor='')
        
        # Remove visual feedback
        self.header_frame.configure(bg=Colors.DARK_GREEN)
        
        # Update the stored height
        self.menu_height = self.winfo_height()
        
        # Save the new height persistently
        self.links_manager.set_menu_height(self.menu_height)
        
        print(f"Resize ended: new height={self.menu_height} (saved)")
    
    # Drag and Drop Event Handlers
    def on_link_press(self, event, link, index):
        """Handle mouse press on link - start potential drag or prepare for click"""
        import time
        self.drag_start_time = time.time() * 1000  # Convert to milliseconds
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.dragged_link_data = link
        self.dragged_link_index = index
        self.potential_drag = True
        
        # Schedule a delayed check for click vs drag
        self.after(self.drag_time_threshold, lambda: self.check_for_click_or_drag(event, link, index))
    
    def on_link_drag(self, event, link, index):
        """Handle mouse drag on link"""
        if not hasattr(self, 'potential_drag') or not self.potential_drag:
            return
        
        # Calculate distance moved
        distance = ((event.x_root - self.drag_start_x) ** 2 + (event.y_root - self.drag_start_y) ** 2) ** 0.5
        
        if distance > self.drag_threshold:
            self.start_link_drag(event, link, index)
    
    def on_link_release(self, event, link, index):
        """Handle mouse release on link"""
        if self.is_dragging_link:
            self.end_link_drag(event, link, index)
        elif hasattr(self, 'potential_drag') and self.potential_drag:
            # This was a click, not a drag
            self.handle_link_click(link)
        
        # Reset drag state
        self.potential_drag = False
        self.is_dragging_link = False
    
    def check_for_click_or_drag(self, event, link, index):
        """Determine if this was a click or start of drag after delay"""
        if hasattr(self, 'potential_drag') and self.potential_drag and not self.is_dragging_link:
            # Still within time threshold and no drag started, treat as click
            pass  # Let the release handler manage the click
    
    def handle_link_click(self, link):
        """Handle regular link click to open file"""
        FileUtils.open_path(link['path'], self.parent)
        self.destroy()
    
    def start_link_drag(self, event, link, index):
        """Start dragging a link"""
        if self.is_dragging_link:
            return
        
        self.is_dragging_link = True
        self.potential_drag = False
        
        # Create drag visual
        self.create_drag_visual(event, link)
        
        # Show drop indicators
        self.show_drop_indicators()
        
        print(f"Started dragging: {link['name']}")
    
    def create_drag_visual(self, event, link):
        """Create visual feedback for dragging"""
        if self.drag_visual:
            self.drag_visual.destroy()
        
        self.drag_visual = tk.Toplevel(self)
        self.drag_visual.overrideredirect(True)
        self.drag_visual.attributes('-topmost', True)
        self.drag_visual.attributes('-alpha', 0.8)
        
        # Make drag visual ignore mouse events (so they pass through to drop zones)
        try:
            # This makes the window transparent to mouse events
            self.drag_visual.attributes('-transparentcolor', 'black')  
        except:
            pass  # Not all systems support this
        
        # Create drag visual content
        drag_frame = tk.Frame(self.drag_visual, bg=Colors.DARK_GREEN, relief=tk.RAISED, bd=2)
        drag_frame.pack(padx=2, pady=2)
        
        tk.Label(drag_frame, text=f"🚀 {link['name']}", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                font=Fonts.MENU_ITEM, padx=10, pady=5).pack()
        
        # Position at cursor
        self.drag_visual.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        
        # Bind motion to follow cursor
        self.bind("<Motion>", self.update_drag_visual)
    
    def update_drag_visual(self, event):
        """Update drag visual position"""
        if self.drag_visual and self.is_dragging_link:
            self.drag_visual.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
    
    def show_drop_indicators(self):
        """Show visual indicators for valid drop zones"""
        # This would highlight valid drop areas
        # For now, we'll rely on hover effects in the drop zone handlers
        pass
    
    def end_link_drag(self, event, link, index):
        """End link drag operation"""
        print(f"Ending drag for: {link['name']}")
        
        # Try to find drop target at current mouse position
        drop_target = self.find_drop_target_at_position(event.x_root, event.y_root)
        
        if drop_target:
            print(f"Found drop target: {drop_target}")
            self.current_drop_target = drop_target
            self.perform_drop_operation()
        else:
            print("No valid drop target found")
        
        self.is_dragging_link = False
        
        # Clean up drag visual
        if self.drag_visual:
            self.drag_visual.destroy()
            self.drag_visual = None
        
        # Unbind motion events
        self.unbind("<Motion>")
        
        # Hide drop indicators
        self.hide_drop_indicators()
        
        print(f"Ended dragging: {link['name']}")
    
    def hide_drop_indicators(self):
        """Hide drop zone indicators"""
        # Clean up any drop indicators
        for indicator in self.drop_indicators:
            try:
                indicator.destroy()
            except:
                pass
        self.drop_indicators.clear()
    
    # Drop Zone Event Handlers
    def on_drop_zone_enter(self, event, link, index):
        """Handle mouse entering a link drop zone"""
        if self.is_dragging_link and self.dragged_link_index != index:
            event.widget.configure(bg=Colors.HOVER_GREEN)
            self.current_drop_target = {'type': 'reorder', 'link': link, 'index': index}
    
    def on_drop_zone_leave(self, event, link, index):
        """Handle mouse leaving a link drop zone"""
        if self.is_dragging_link:
            event.widget.configure(bg=Colors.LIGHT_GREEN)
            if hasattr(self, 'current_drop_target'):
                delattr(self, 'current_drop_target')
    
    def on_category_drop_zone_enter(self, event, category):
        """Handle mouse entering a category drop zone"""
        if self.is_dragging_link and self.dragged_link_data['category'] != category:
            event.widget.configure(bg=Colors.MEDIUM_GREEN)
            self.current_drop_target = {'type': 'move', 'category': category}
    
    def on_category_drop_zone_leave(self, event, category):
        """Handle mouse leaving a category drop zone"""
        if self.is_dragging_link:
            event.widget.configure(bg=Colors.LIGHT_GREEN)
            if hasattr(self, 'current_drop_target'):
                delattr(self, 'current_drop_target')
    
    def on_empty_category_enter(self, event, category):
        """Handle mouse entering an empty category"""
        if self.is_dragging_link and self.dragged_link_data['category'] != category:
            event.widget.configure(bg=Colors.MEDIUM_GREEN)
            self.current_drop_target = {'type': 'move', 'category': category}
    
    def on_empty_category_leave(self, event, category):
        """Handle mouse leaving an empty category"""
        if self.is_dragging_link:
            event.widget.configure(bg=Colors.LIGHT_GREEN)
            if hasattr(self, 'current_drop_target'):
                delattr(self, 'current_drop_target')
    
    def perform_drop_operation(self):
        """Perform the actual drop operation based on current target"""
        print(f"Performing drop operation...")
        
        if not hasattr(self, 'current_drop_target'):
            print("No current_drop_target found")
            return False
            
        if not self.dragged_link_data or self.dragged_link_index is None:
            print("No dragged link data found")
            return False
        
        target = self.current_drop_target
        success = False
        
        print(f"Drop target: {target}")
        print(f"Dragged link: {self.dragged_link_data['name']} (index: {self.dragged_link_index})")
        
        if target['type'] == 'move':
            # Move to different category
            print(f"Attempting to move to category: {target['category']}")
            success = self.links_manager.move_link_to_category(self.dragged_link_index, target['category'])
            if success:
                print(f"✅ Moved '{self.dragged_link_data['name']}' to category '{target['category']}'")
            else:
                print(f"❌ Failed to move '{self.dragged_link_data['name']}' to category '{target['category']}'")
        
        elif target['type'] == 'reorder':
            # Reorder within same category
            dragged_category = self.dragged_link_data['category']
            dragged_pos = self.links_manager.get_link_position_in_category(self.dragged_link_index)
            target_pos = self.links_manager.get_link_position_in_category(target['index'])
            
            print(f"Attempting to reorder in category: {dragged_category}")
            print(f"From position {dragged_pos} to position {target_pos}")
            
            if dragged_pos != -1 and target_pos != -1:
                success = self.links_manager.reorder_links_in_category(dragged_category, dragged_pos, target_pos)
                if success:
                    print(f"✅ Reordered '{self.dragged_link_data['name']}' in category '{dragged_category}'")
                else:
                    print(f"❌ Failed to reorder '{self.dragged_link_data['name']}' in category '{dragged_category}'")
            else:
                print(f"❌ Invalid positions: dragged_pos={dragged_pos}, target_pos={target_pos}")
        
        if success:
            # Refresh the menu to show changes
            print("Refreshing menu...")
            self.refresh_menu()
        else:
            print("Drop operation failed")
        
        return success
    
    def refresh_menu(self):
        """Refresh the menu display after drag and drop operations"""
        # Store current position
        current_x = self.winfo_x()
        current_y = self.winfo_y()
        current_height = self.winfo_height()
        
        # Recreate the column layout
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.create_column_layout()
        
        # Restore position and size
        self.geometry(f"{self.menu_width}x{current_height}+{current_x}+{current_y}")
        
        print("Menu refreshed after drag and drop")
    
    def find_drop_target_at_position(self, x, y):
        """Find what widget/drop target is at the given screen coordinates"""
        try:
            # Get widget at position relative to this window
            widget_at_pos = self.winfo_containing(x, y)
            
            if not widget_at_pos:
                return None
                
            print(f"Widget at position: {widget_at_pos}")
            
            # Check if it's a link (for reordering)
            if hasattr(widget_at_pos, 'link_data') and hasattr(widget_at_pos, 'link_index'):
                link_data = widget_at_pos.link_data
                link_index = widget_at_pos.link_index
                
                # Don't allow dropping on self
                if link_index == self.dragged_link_index:
                    return None
                    
                return {
                    'type': 'reorder', 
                    'link': link_data, 
                    'index': link_index
                }
            
            # Check if it's a category area (for moving to different category)
            if hasattr(widget_at_pos, 'category'):
                category = widget_at_pos.category
                
                # Don't allow dropping in same category (unless it's for reordering)
                if category != self.dragged_link_data['category']:
                    return {
                        'type': 'move', 
                        'category': category
                    }
            
            # Check parent widgets for category info
            parent = widget_at_pos
            while parent and parent != self:
                if hasattr(parent, 'category'):
                    category = parent.category
                    if category != self.dragged_link_data['category']:
                        return {
                            'type': 'move', 
                            'category': category
                        }
                parent = parent.master
                
            return None
            
        except Exception as e:
            print(f"Error finding drop target: {e}")
            return None

class AddEditLinkDialog(CustomDialog):
    """Dialog for adding or editing links"""
    
    def __init__(self, parent, links_manager, taskbar_instance, edit_mode=False, link_data=None, link_index=None):
        title = "Edit Link" if edit_mode else "Add New Link"
        super().__init__(parent, title, width=450, height=280)
        
        self.links_manager = links_manager
        self.taskbar_instance = taskbar_instance
        self.edit_mode = edit_mode
        self.link_data = link_data
        self.link_index = link_index
        
        self.create_form()
        self.add_buttons()
        
        # Prefill data if editing
        if edit_mode and link_data:
            self.name_field.set(link_data['name'])
            self.path_field.set(link_data['path'])
            self.category_field.set(link_data['category'])
    
    def create_form(self):
        """Create the form fields"""
        # Name field
        self.name_field = FormField(self.dialog_content, "Name:", width=35)
        self.name_field.pack(fill=tk.X, pady=5)
        
        # Path field with browse button
        path_frame = tk.Frame(self.dialog_content, bg=Colors.LIGHT_GREEN)
        path_frame.pack(fill=tk.X, pady=5)
        
        self.path_field = FormField(path_frame, "Path/URL:", width=25)
        self.path_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(path_frame, text="Browse...", command=self.browse_path,
                              bg=Colors.MEDIUM_GREEN, font=Fonts.DIALOG_LABEL)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Category field
        self.category_field = FormField(
            self.dialog_content, "Category:", 
            field_type='combobox',
            values=self.links_manager.get_categories(),
        )
        self.category_field.pack(fill=tk.X, pady=5)
        
        # Set default category to "Quick Links"
        categories = self.links_manager.get_categories()
        if "Quick Links" in categories:
            self.category_field.set("Quick Links")
        elif categories:
            self.category_field.set(categories[0])
    
    def browse_path(self):
        """Browse for file or folder"""
        import os
        
        self.grab_release()
        choice = BrowseChoiceDialog.ask(self)
        
        if choice == "file":
            path = filedialog.askopenfilename(parent=self)
        elif choice == "folder":
            path = filedialog.askdirectory(parent=self)
        else:
            # Restore grab and focus when canceling
            self.grab_set()
            self.focus_force()
            return
        
        if path:
            self.path_field.set(path)
            
            # Auto-populate name field if it's empty
            if not self.name_field.get().strip():
                if choice == "file":
                    # Extract filename without extension
                    filename = os.path.basename(path)
                    name_without_ext = os.path.splitext(filename)[0]
                    self.name_field.set(name_without_ext)
                elif choice == "folder":
                    # Extract folder name
                    folder_name = os.path.basename(path.rstrip(os.sep))
                    self.name_field.set(folder_name)
        
        # Always restore grab and focus after browse operation
        self.grab_set()
        self.focus_force()
    
    def add_buttons(self):
        """Add Save and Cancel buttons"""
        button_container = tk.Frame(self.button_frame, bg=Colors.LIGHT_GREEN)
        button_container.pack(expand=True)
        
        save_btn = tk.Button(button_container, text="Save", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                            command=self.save_link, width=Dimensions.DIALOG_BUTTON_WIDTH,
                            font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_container, text="Cancel", bg=Colors.INACTIVE_GRAY, fg=Colors.WHITE,
                              command=self.cancel, width=Dimensions.DIALOG_BUTTON_WIDTH,
                              font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def save_link(self):
        """Save the link"""
        name = self.name_field.get().strip()
        path = self.path_field.get().strip()
        category = self.category_field.get()
        
        if not name or not path:
            WarningDialog.show(self, "Invalid Input", "Please enter both name and path.")
            return
        
        if self.edit_mode:
            # Update existing link
            icon = self.link_data.get('icon', '📄') if self.link_data else '📄'
            success = self.links_manager.update_link(self.link_index, name, path, category, icon)
        else:
            # Add new link
            success = self.links_manager.add_link(name, path, category)
        
        if success:
            self.destroy()
            # Refresh menu
            self.taskbar_instance.show_links_menu(None)
        else:
            ErrorDialog.show(self, "Error", "Failed to save link.")
    
    @classmethod
    def show_add_dialog(cls, parent, links_manager, taskbar_instance):
        """Show dialog to add a new link"""
        dialog = cls(parent, links_manager, taskbar_instance)
        dialog.lift()
        dialog.focus_force()
        return dialog
    
    @classmethod
    def show_edit_dialog(cls, parent, links_manager, taskbar_instance, link_data, link_index):
        """Show dialog to edit an existing link"""
        dialog = cls(parent, links_manager, taskbar_instance, True, link_data, link_index)
        dialog.lift()
        dialog.focus_force()
        return dialog

class BrowseChoiceDialog(CustomDialog):
    """Custom dialog for choosing between file or folder browsing"""
    
    def __init__(self, parent):
        super().__init__(parent, "Browse Options", width=300, height=180)
        
        # Icon and message
        icon_label = tk.Label(self.dialog_content, text="📁", bg=Colors.LIGHT_GREEN,
                             fg=Colors.BLACK, font=('Arial', 24))
        icon_label.pack(pady=10)
        
        message_label = tk.Label(self.dialog_content, text="What would you like to browse for?", 
                               bg=Colors.LIGHT_GREEN, fg=Colors.BLACK, font=Fonts.DIALOG_LABEL)
        message_label.pack(pady=5)
        
        # Add buttons
        self.add_choice_buttons()
        
        # Bind keys
        self.bind('<Escape>', lambda e: self.cancel())
    
    def add_choice_buttons(self):
        """Add File, Folder, and Cancel buttons"""
        button_container = tk.Frame(self.button_frame, bg=Colors.LIGHT_GREEN)
        button_container.pack(expand=True)
        
        # File button
        file_btn = tk.Button(button_container, text="File", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                           command=self.choose_file, width=8,
                           font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        file_btn.pack(side=tk.LEFT, padx=5)
        
        # Folder button
        folder_btn = tk.Button(button_container, text="Folder", bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK,
                             command=self.choose_folder, width=8,
                             font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(button_container, text="Cancel", bg=Colors.INACTIVE_GRAY, fg=Colors.WHITE,
                             command=self.cancel, width=8,
                             font=Fonts.DIALOG_BUTTON, relief=tk.RAISED, bd=1)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Focus on File button as default
        file_btn.focus_set()
    
    def choose_file(self):
        """File button clicked"""
        self.result = "file"
        self.destroy()
    
    def choose_folder(self):
        """Folder button clicked"""
        self.result = "folder"
        self.destroy()
    
    @classmethod
    def ask(cls, parent):
        """Show browse choice dialog and return result"""
        dialog = cls(parent)
        dialog.lift()
        dialog.focus_force()
        try:
            parent.wait_window(dialog)
            return dialog.result
        finally:
            # Ensure parent regains focus after dialog closes
            if parent and parent.winfo_exists():
                parent.focus_force()