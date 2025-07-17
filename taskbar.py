# taskbar.py (UPDATED)
"""
Core taskbar window and layout for SuiteView Taskbar Application
"""

import tkinter as tk
from tkinter import ttk
import sys
from ctypes import wintypes

from config import Colors, Fonts, Dimensions, Settings
from utils import WindowsUtils, UIUtils
from links_manager import LinksManager
from quick_links import QuickLinksMenu
from snip_feature import add_snip_feature_to_taskbar
from folder_inventory import FolderInventoryDialog, FolderInventoryWindow

from window_manager import WindowManager
from windows_menu import WindowsMenu
from pinned_windows import PinnedWindowsSection
from simple_window_factory import SimpleWindow

class SuiteViewTaskbar:
    """Main taskbar application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.links_manager = LinksManager()
        self.window_manager = WindowManager()

        # Initialize these BEFORE creating UI
        self.links_menu = None
        self.windows_menu = None
        self.pinned_section = None  # Initialize to None
        self.windows_menu_geometry = None
        self.email_options_menu = None  # Initialize email options menu tracker
        self.email_menu_closing = False  # Flag to prevent immediate reopen
        self.emails_btn = None
        
        # Store original work area for restoration
        self.original_work_area = WindowsUtils.get_work_area()
        
        # Get screen dimensions
        self.screen_width, self.screen_height = WindowsUtils.get_screen_dimensions()
        
        # Get Windows taskbar height for better positioning
        self.windows_taskbar_height = WindowsUtils.get_windows_taskbar_height()
        
        # Position the custom taskbar above Windows taskbar
        self.y_position = self.screen_height - self.windows_taskbar_height - Dimensions.TASKBAR_HEIGHT
        
        # Setup the window
        self.setup_window()
        
        # Create taskbar content
        self.create_taskbar_content()
        
        # Setup event bindings
        self.bind_events()
        
        # Apply Windows API modifications
        self.setup_windows_integration()
        
        # Initialize test window as None (will be created when Test button is clicked)
        self.test_window = None
               
        
    def setup_window(self):
        """Configure the main window properties"""
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Set window attributes
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', Settings.TASKBAR_OPACITY)
        
        # Configure window geometry
        self.root.geometry(f"{self.screen_width}x{Dimensions.TASKBAR_HEIGHT}+0+{self.y_position}")
        
        # Set background color to dark green
        self.root.configure(bg=Colors.DARK_GREEN)
    
    def create_taskbar_content(self):
        """Create the taskbar UI elements"""
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg=Colors.DARK_GREEN, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # SuiteView Logo/Title
        self.create_logo_section()
        
        # Separator
        separator = UIUtils.create_separator(self.main_frame, Colors.DARK_GREEN, width=2)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Main buttons
        self.create_main_buttons()
        
        # Right side elements
        self.create_right_side_elements()
    
    def create_logo_section(self):
        """Create the SuiteView logo/title section"""
        logo_frame = tk.Frame(self.main_frame, bg=Colors.DARK_GREEN)
        logo_frame.pack(side=tk.LEFT, padx=10)
        
        # Logo text with styling
        logo_label = tk.Label(logo_frame, text=Settings.APP_NAME, bg=Colors.DARK_GREEN, 
                             fg=Colors.WHITE, font=Fonts.TASKBAR_TITLE)
        logo_label.pack()
        logo_label.bind("<Button-3>", self.show_links_menu)
    
    def create_main_buttons(self):
        """Create the main taskbar buttons"""
        # Existing buttons
        buttons_data = [
            ("Get Policy", None),
            ("Cyber", None),
            ("TAI", None)
        ]
        
        for text, command in buttons_data:
            btn = tk.Button(self.main_frame, text=text, bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                        relief=tk.FLAT, font=Fonts.TASKBAR_BUTTON, cursor='hand2',
                        activebackground=Colors.HOVER_GREEN, bd=0, padx=15)
            btn.pack(side=tk.LEFT, padx=5)
            btn.bind("<Button-3>", self.show_links_menu)
            if command:
                btn.configure(command=command)
        
        # Add separator before new features
        separator = UIUtils.create_separator(self.main_frame, Colors.DARK_GREEN, width=2)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Add separator before Snip feature
        separator2 = UIUtils.create_separator(self.main_frame, Colors.DARK_GREEN, width=2)
        separator2.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Inventory button
        inventory_btn = tk.Button(self.main_frame, text="Inventory", 
                                bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                                relief=tk.FLAT, font=Fonts.TASKBAR_BUTTON, 
                                cursor='hand2', activebackground=Colors.HOVER_GREEN, 
                                bd=0, padx=15, command=self.show_inventory_dialog)
        inventory_btn.pack(side=tk.LEFT, padx=5)

        # Add separator before Snip feature
        separator3 = UIUtils.create_separator(self.main_frame, Colors.DARK_GREEN, width=2)
        separator3.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Snip button
        self.snipping_manager = add_snip_feature_to_taskbar(self)

        # Add separator 
        separator4 = UIUtils.create_separator(self.main_frame, Colors.DARK_GREEN, width=2)
        separator4.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        #Test window button
        self.test_window_btn = tk.Button(self.main_frame, text="Test", 
                                bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                                relief=tk.FLAT, font=Fonts.TASKBAR_BUTTON, 
                                cursor='hand2', activebackground=Colors.HOVER_GREEN, 
                                bd=0, padx=15, command=self.show_test_window)
        self.test_window_btn.pack(side=tk.LEFT, padx=5)  

        # Add separator before pinned windows section
        separator3 = UIUtils.create_separator(self.main_frame, Colors.DARK_GREEN, width=2)
        separator3.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        

        # Create and store pinned windows section
        print(f"Creating pinned section...")
        self.pinned_section = PinnedWindowsSection(self.main_frame, self.window_manager, self.on_windows_pinned)
        self.pinned_section.pack(side=tk.LEFT, fill=tk.Y)  # Remove padx, let it grow as needed
        
        # Debug to confirm it's created and assigned
        #print(f"Pinned section created and assigned: {self.pinned_section}")
        #print(f"self.pinned_section is not None: {self.pinned_section is not None}")
    
    def create_right_side_elements(self):
        """Create the right side elements of the taskbar"""
        
        # X close button
        close_btn = tk.Label(self.main_frame, text="X", bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                            font=(Fonts.TASKBAR_BUTTON[0], Fonts.TASKBAR_BUTTON[1], 'bold'), 
                            cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=5)
        close_btn.bind("<Button-1>", self.close_app)
    
        #Windows button
        windows_btn = tk.Button(self.main_frame, text="Windows", 
                            bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                            relief=tk.FLAT, font=Fonts.TASKBAR_BUTTON, 
                            cursor='hand2', activebackground=Colors.HOVER_GREEN, 
                            bd=0, padx=15, command=self.toggle_windows_menu)
        windows_btn.pack(side=tk.RIGHT, padx=5)

        
        # Add Emails button
        self.emails_btn = tk.Button(self.main_frame, text="Emails", 
                        bg=Colors.DARK_GREEN, fg=Colors.WHITE,
                        relief=tk.FLAT, font=Fonts.TASKBAR_BUTTON, 
                        cursor='hand2', activebackground=Colors.HOVER_GREEN, 
                        bd=0, padx=15, command=self.show_email_options_menu)
        self.emails_btn.pack(side=tk.LEFT, padx=5)

    def bind_events(self):
        """Bind event handlers"""
        # Main window events
        self.root.bind("<Button-3>", self.show_links_menu)
        self.main_frame.bind("<Button-3>", self.show_links_menu)
        
        # Emergency exit keys
        self.root.bind("<Escape>", self.close_app)
        self.root.bind("<Control-q>", self.close_app)
        self.root.bind("<Control-Q>", self.close_app)
        self.root.bind("<Alt-F4>", self.close_app)
    
    def setup_windows_integration(self):
        """Setup Windows API integration"""
        # Keep window on top using Windows API
        self.set_always_on_top()
        
        # Adjust desktop working area
        self.adjust_work_area()
        
    def show_links_menu(self, event):
        """Show the right-click links menu positioned above the taskbar"""
        if self.links_menu:
            self.links_menu.destroy()
        
        # Create the menu at a temporary position first
        temp_x, temp_y = 0, 0
        self.links_menu = QuickLinksMenu(self.root, self, temp_x, temp_y)
        
        # Get cursor position or use center position
        if event:
            x = self.root.winfo_pointerx() - 200  # Offset to center menu on cursor
        else:
            x = self.screen_width // 2 - 200  # Center horizontally
        
        # Calculate proper position above YOUR custom taskbar
        final_y = self.y_position - self.links_menu.menu_height - 5  # 5px gap above YOUR taskbar
        final_x = x
        
        # Reposition the menu to the correct location
        self.links_menu.geometry(f"+{final_x}+{final_y}")
        
        # Debug output
        print(f"Estimated height: {self.links_menu.menu_height}")
        print(f"Positioned menu at: {final_x}, {final_y}")
        print(f"Menu bottom should be at: {final_y + self.links_menu.menu_height}")
       
    def show_windows_menu(self, event=None):
        """Show the windows management menu - toggle if already open"""
        if self.windows_menu and self.windows_menu.winfo_exists():
            # If menu exists and is open, close it
            self.windows_menu.close_window()
            self.windows_menu = None
        else:
            # Otherwise, create and show it
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            
            # Position the menu above the taskbar, centered on screen
            x = (screen_width - 700) // 2  # Center a 700px wide menu
            y = self.y_position - 600  # Default height assumption
            
    def set_always_on_top(self):
        """Force window to stay on top using Windows API"""
        WindowsUtils.set_window_topmost(self.root.winfo_id())
    
    def adjust_work_area(self):
        """Adjust desktop work area to make room for taskbar"""
        if self.original_work_area:
            work_area = wintypes.RECT()
            work_area.left = self.original_work_area.left
            work_area.top = self.original_work_area.top
            work_area.right = self.original_work_area.right
            work_area.bottom = self.y_position
            
            success = WindowsUtils.set_work_area(work_area)
            if not success:
                print("Could not adjust work area. May require admin privileges.")
    
    def close_app(self, event=None):
        """Close the application"""
        try:
            self.window_manager.unhide_all_windows()
            self.restore_work_area()
        except:
            pass  # Don't fail if restore doesn't work
        
        # Clean up snipping manager if it exists
        if hasattr(self, 'snipping_manager'):
            try:
                self.snipping_manager.cleanup_temp_directory()
            except:
                pass
        
        # Force kill any open dialogs
        for child in self.root.winfo_children():
            if isinstance(child, tk.Toplevel):
                child.destroy()
        
        self.root.quit()
        self.root.destroy()
        sys.exit(0)
    
    def restore_work_area(self):
        """Restore original work area"""
        if self.original_work_area:
            WindowsUtils.restore_work_area(self.original_work_area)
    
    def run(self):
        """Start the application"""
        """Start the application"""
        
        # Start the periodic topmost maintenance
        #self.root.after(Settings.AUTO_REFRESH_INTERVAL, self.maintain_topmost)
        
        # Start window state monitoring
        self.root.after(1000, self.start_window_monitoring)  # Start after 1 second

        # Start the main event loop
        self.root.mainloop()
    
    def maintain_topmost(self):
        """Periodically ensure window stays on top"""
        self.set_always_on_top()

        # # Update pinned window button states
        # if self.pinned_section:
        #     self.pinned_section.update_window_states()

        self.root.after(Settings.AUTO_REFRESH_INTERVAL, self.maintain_topmost)

    def toggle_windows_menu(self):
        """Toggle the windows management menu"""
        if self.windows_menu and hasattr(self.windows_menu, 'winfo_exists'):
            try:
                if self.windows_menu.winfo_exists():
                    # Store current geometry BEFORE closing
                    self.windows_menu_geometry = self.windows_menu.get_current_geometry()
                    print(f"Storing geometry: {self.windows_menu_geometry}")  # Debug
                    self.windows_menu.close_window()
                    self.windows_menu = None
                    return
            except:
                self.windows_menu = None
        
        # Create new windows menu
        print(f"Class: {type(self).__name__}")  # Debug
        self.windows_menu = WindowsMenu(self, self.window_manager, 
                                    self.on_windows_pinned,
                                    self.windows_menu_geometry)
    
    def on_windows_pinned(self):
        """Callback when windows are pinned/unpinned"""
        #print(f"\n=== ON_WINDOWS_PINNED CALLED ===")
        #print(f"Pinned section: {self.pinned_section}")
        
        if self.pinned_section:
            print(f"Refreshing pinned section...")
            self.pinned_section.refresh()
        else:
            print(f"ERROR: pinned_section is None!")
        
        # Always refresh the Windows Manager if it's open to update the list
        if self.windows_menu and hasattr(self.windows_menu, 'winfo_exists'):
            try:
                if self.windows_menu.winfo_exists():
                    print(f"Refreshing Windows Manager...")
                    self.windows_menu.refresh_window_list()
                else:
                    print(f"Windows Manager exists but window is destroyed")
            except Exception as e:
                print(f"Error refreshing Windows Manager: {e}")
                self.windows_menu = None
        else:
            print(f"Windows Manager is not open")
            
        #print(f"=== END ON_WINDOWS_PINNED ===\n")


    def start_window_monitoring(self):
        """Start monitoring for closed windows"""
        self.check_window_states()
        
    def check_window_states(self):
        """Periodically check if pinned windows still exist"""
        try:
            if hasattr(self, 'pinned_section') and self.pinned_section:
                # Get current pinned windows
                pinned_windows = self.window_manager.get_pinned_windows()
                windows_to_unpin = []
                
                for window in pinned_windows:
                    # Check if window still exists
                    if not window.is_valid():
                        print(f"Window {window.display_name} no longer exists, unpinning...")
                        windows_to_unpin.append(window)
                
                # Unpin any closed windows
                if windows_to_unpin:
                    for window in windows_to_unpin:
                        self.window_manager.unpin_window(window)
                    
                    # Refresh the pinned section
                    self.pinned_section.refresh()
                    
                    # Also refresh Windows Manager if it's open
                    if hasattr(self, 'windows_menu') and self.windows_menu:
                        try:
                            if self.windows_menu.winfo_exists():
                                self.windows_menu.refresh_window_list()
                        except:
                            pass
        
        except Exception as e:
            print(f"Error checking window states: {e}")
        
        # Schedule next check (every 2 seconds)
        self.root.after(2000, self.check_window_states)

    def verify_setup(self):
        """Verify all components are properly initialized"""
        print(f"\n=== VERIFYING TASKBAR SETUP ===")
        print(f"Window manager: {self.window_manager}")
        print(f"Pinned section: {self.pinned_section}")
        print(f"Pinned section type: {type(self.pinned_section)}")
        if self.pinned_section:
            print(f"Pinned section parent: {self.pinned_section.master}")
            print(f"Pinned section visible: {self.pinned_section.winfo_exists()}")
        print(f"=== END VERIFICATION ===\n")
    
    def check_window_states(self):
        """Periodically check for closed windows, new windows, and title changes"""
        try:
            # Get current window list
            current_windows = self.window_manager.get_relevant_windows()
            current_hwnds = {w.hwnd for w in current_windows}
            
            # Check for closed pinned windows
            if hasattr(self, 'pinned_section') and self.pinned_section:
                pinned_windows = self.window_manager.get_pinned_windows()
                windows_to_unpin = []
                
                for window in pinned_windows:
                    if not window.is_valid():
                        print(f"Window {window.display_name} no longer exists, unpinning...")
                        windows_to_unpin.append(window)
                
                if windows_to_unpin:
                    for window in windows_to_unpin:
                        self.window_manager.unpin_window(window)
                    self.pinned_section.refresh()
            
            # Initialize tracking dictionaries if they don't exist
            if not hasattr(self, '_previous_hwnds'):
                self._previous_hwnds = current_hwnds
                self._window_titles = {}
            
            # Check for new windows
            new_hwnds = current_hwnds - self._previous_hwnds
            if new_hwnds:
                print(f"Detected {len(new_hwnds)} new window(s)")
                self._refresh_windows_menu()
            
            # Check for title changes in existing windows
            title_changed = False
            for window in current_windows:
                hwnd = window.hwnd
                current_title = window.title
                
                # Store or compare title
                if hwnd in self._window_titles:
                    if self._window_titles[hwnd] != current_title:
                        #print(f"Title changed for {window.app_name}: '{self._window_titles[hwnd]}' -> '{current_title}'")
                        title_changed = True
                        self._window_titles[hwnd] = current_title
                        
                        # Update the window's display name
                        window.display_name = window._create_display_name()
                        
                        # Update pinned button if this window is pinned
                        if window.is_pinned and hasattr(self, 'pinned_section') and self.pinned_section:
                            self.pinned_section.update_window_title(window)
                else:
                    self._window_titles[hwnd] = current_title
            
            # Clean up titles for closed windows
            closed_hwnds = set(self._window_titles.keys()) - current_hwnds
            for hwnd in closed_hwnds:
                del self._window_titles[hwnd]
            
            # Refresh Windows menu if titles changed
            if title_changed:
                self._refresh_windows_menu()
            
            # Update previous list for next check
            self._previous_hwnds = current_hwnds
        
        except Exception as e:
            print(f"Error checking window states: {e}")
        
        # Schedule next check (every 1 second for responsive updates)
        self.root.after(1000, self.check_window_states)

    def _refresh_windows_menu(self):
        """Helper method to refresh Windows menu if it's open"""
        if hasattr(self, 'windows_menu') and self.windows_menu:
            try:
                if self.windows_menu.winfo_exists():
                    print("Refreshing Windows Manager...")
                    self.windows_menu.refresh_window_list()
            except:
                pass

    def show_test_window(self):
        """Show the test window - create it if it doesn't exist, or toggle it if it does"""
        # Check if window exists and is valid
        if self.test_window is None or not self.test_window.winfo_exists():
            # Create a new test window with session persistence and toggle functionality
            self.test_window = SimpleWindow(
                self.root,
                title="Test Window", 
                resize_handles=["left", "right", "bottom", "top"], 
                movable=True, 
                location_persistence="session",
                close_on=["x_button", "toggle"]
            )
            
            # Register the Test button as a toggle control
            self.test_window.register_toggle_control(self.test_window_btn)
            
            # Add some content to the test window so it's not empty
            test_label = tk.Label(
                self.test_window.get_content_frame(), 
                text="This is a test window\nYou can resize it from any edge\nYou can also drag it around\n\nWindow position and size will be remembered\nwhen you close and reopen it\n\nClick the Test button again to close this window",
                bg=Colors.DARK_GREEN, 
                fg=Colors.WHITE,
                font=("Arial", 10), 
                justify=tk.CENTER
            )
            test_label.pack(expand=True, padx=20, pady=20)
        
        # Show and focus the window (this will be handled by toggle functionality)
        self.test_window.lift()
        self.test_window.focus_force()
    
    
    def show_inventory_dialog(self):
        """Show the folder inventory dialog"""
        dialog = FolderInventoryDialog(self.root)
        dialog.lift()
        dialog.focus_force()
        
    def show_email_options_menu(self):
        """Show the email options popup menu - toggle if already open"""
        from email_options_menu import EmailOptionsMenu
        
        # # Check if we're in the process of closing (prevents immediate reopen)
        # if hasattr(self, 'email_menu_closing') and self.email_menu_closing:
        #     return
        
        # # Check if email options menu is already open
        # if hasattr(self, 'email_options_menu') and self.email_options_menu is not None:
        #     try:
        #         # Note: Need to check self.email_options_menu.root since that's the actual window
        #         if self.email_options_menu.root.winfo_exists():
        #             # Menu is open, close it
        #             self.email_options_menu.root.destroy()
        #             self.email_options_menu = None
        #             return
        #     except:
        #         self.email_options_menu = None
        
        
        if self.emails_btn:
            # Create and show the options menu
            self.email_options_menu = EmailOptionsMenu(self.root, self.emails_btn, self)
            
            # Position menu above taskbar
            menu_height = 150  # Approximate height for 2 menu items
            x = self.emails_btn.winfo_rootx()
            taskbar_top = self.root.winfo_rooty()
            y = taskbar_top - menu_height
            
            # Set the position
            self.email_options_menu.geometry(f"{200}x{menu_height}+{x}+{y}")
            
            # Set up cleanup when menu is destroyed
            def cleanup():
                self.email_options_menu = None
            
            self.email_options_menu.bind("<Destroy>", lambda e: cleanup())
