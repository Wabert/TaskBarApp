# config.py
"""
Configuration constants for SuiteView Taskbar Application
Contains colors, sizes, paths, and other application settings
"""

from pathlib import Path

# Color Scheme (Two-Tone Green)
class Colors:
    DARK_GREEN = '#006600'      # Main taskbar, headers, borders
    MEDIUM_GREEN = '#00AA00'    # Menu backgrounds, inactive elements  
    LIGHT_GREEN = '#B3FFB3'     # Input fields, hover states, active elements (lighter green)
    #LIGHT_GREEN = '#00CC00'
    HOVER_GREEN = '#008800'     # Hover effects
    INACTIVE_GRAY = '#666666'   # Cancel buttons, disabled elements
    WHITE = '#FFFFFF'
    BLACK = '#000000'

    WINDOW_HIDDEN = '#FF6666'      # Red tint for hidden windows
    WINDOW_VISIBLE = '#66FF66'     # Green tint for visible windows
    PINNED_SECTION_BG = '#004400'  # Darker green for pinned section
    PIN_BUTTON_COLOR = '#FFFF00'   # Yellow for pin buttons

# Font Settings
class Fonts:
    TASKBAR_TITLE = ('Arial', 14, 'bold italic')
    TASKBAR_BUTTON = ('Arial', 10)
    MENU_HEADER = ('Arial', 10, 'bold')
    MENU_ITEM = ('Arial', 8)
    DIALOG_TITLE = ('Arial', 10, 'bold')
    DIALOG_LABEL = ('Arial', 9)
    DIALOG_BUTTON = ('Arial', 9)
    WARNING_ICON = ('Arial', 20)

# Window Dimensions
class Dimensions:
    TASKBAR_HEIGHT = 40
    MENU_MIN_WIDTH = 400
    MENU_MIN_HEIGHT = 100
    DIALOG_BUTTON_WIDTH = 8
    DIALOG_PADDING = 10

# File Paths
class Paths:
    CONFIG_DIR = Path.home() / '.suiteview'
    LINKS_FILE = CONFIG_DIR / 'links.json'
    
    @classmethod
    def ensure_config_dir(cls):
        """Ensure configuration directory exists"""
        cls.CONFIG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_config_dir_str(cls):
        """Get configuration directory as normalized Windows path string"""
        import os
        return os.path.normpath(str(cls.CONFIG_DIR))
    
    @classmethod
    def get_links_file_str(cls):
        """Get links file path as normalized Windows path string"""
        import os
        return os.path.normpath(str(cls.LINKS_FILE))

# Windows API Constants
class WindowsAPI:
    SPI_SETWORKAREA = 0x002F
    SPI_GETWORKAREA = 0x0030
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SPIF_SENDCHANGE = 0x0002

# Default Categories for Links
DEFAULT_CATEGORIES = ["Quick Links", "Applications", "Folders", "Websites"]

# Application Settings
class Settings:
    APP_NAME = "SuiteView"
    VERSION = "2.0"
    TASKBAR_OPACITY = 0.98
    MENU_OPACITY = 0.98
    AUTO_REFRESH_INTERVAL = 1000  # milliseconds
    PINNED_SECTION_WIDTH = 400     # Width allocated for pinned windows
    PINNED_BUTTON_WIDTH = 80       # Width of each pinned window button