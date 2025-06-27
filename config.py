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
    MENU_MIN_WIDTH = 200
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


class AppColors:
    """Application-specific color schemes"""
    
    # Define app colors with background and appropriate foreground colors
    APP_COLORS = {
        # Microsoft Office
        'winword': {'bg': '#2B579A', 'fg': '#FFFFFF'},      # Word Blue
        'excel': {'bg': '#217346', 'fg': '#FFFFFF'},        # Excel Green
        'powerpnt': {'bg': '#D24726', 'fg': '#FFFFFF'},     # PowerPoint Orange
        'outlook': {'bg': '#0072C6', 'fg': '#FFFFFF'},      # Outlook Blue
        'msaccess': {'bg': '#A4373A', 'fg': '#FFFFFF'},     # Access Red
        'onenote': {'bg': '#7719AA', 'fg': '#FFFFFF'},      # OneNote Purple
        'mspub': {'bg': '#077568', 'fg': '#FFFFFF'},        # Publisher Teal
        'teams': {'bg': '#6264A7', 'fg': '#FFFFFF'},        # Teams Purple
        
        # Browsers
        'chrome': {'bg': '#4285F4', 'fg': '#FFFFFF'},       # Chrome Blue
        'firefox': {'bg': '#FF7139', 'fg': '#FFFFFF'},      # Firefox Orange
        'msedge': {'bg': '#0078D7', 'fg': '#FFFFFF'},       # Edge Blue
        'opera': {'bg': '#FF1B2D', 'fg': '#FFFFFF'},        # Opera Red
        'brave': {'bg': '#FB542B', 'fg': '#FFFFFF'},        # Brave Orange
        
        # Development Tools
        'code': {'bg': '#007ACC', 'fg': '#FFFFFF'},         # VS Code Blue
        'devenv': {'bg': '#5C2D91', 'fg': '#FFFFFF'},       # Visual Studio Purple
        'pycharm64': {'bg': '#21D789', 'fg': '#FFFFFF'},    # PyCharm Green
        'sublime_text': {'bg': '#FF9800', 'fg': '#FFFFFF'}, # Sublime Orange
        'notepad++': {'bg': '#90C53F', 'fg': '#FFFFFF'},    # Notepad++ Green
        'cursor': {'bg': '#000000', 'fg': '#FFFFFF'},       # Cursor AI Black
        
        # File Types/Readers
        'acrobat': {'bg': '#EC1C24', 'fg': '#FFFFFF'},      # Adobe Acrobat Red
        'acrord32': {'bg': '#EC1C24', 'fg': '#FFFFFF'},     # Adobe Reader Red
        
        # Communication
        'slack': {'bg': '#4A154B', 'fg': '#FFFFFF'},        # Slack Purple
        'discord': {'bg': '#5865F2', 'fg': '#FFFFFF'},      # Discord Blurple
        'zoom': {'bg': '#2D8CFF', 'fg': '#FFFFFF'},         # Zoom Blue
        'skype': {'bg': '#00AFF0', 'fg': '#FFFFFF'},        # Skype Blue
        
        # Media/Creative
        'photoshop': {'bg': '#31A8FF', 'fg': '#FFFFFF'},    # Photoshop Blue
        'illustrator': {'bg': '#FF9A00', 'fg': '#FFFFFF'},  # Illustrator Orange
        'premiere': {'bg': '#EA77FF', 'fg': '#000000'},     # Premiere Purple
        'spotify': {'bg': '#1DB954', 'fg': '#FFFFFF'},      # Spotify Green
        'vlc': {'bg': '#FF8800', 'fg': '#FFFFFF'},          # VLC Orange
        
        # System/Utilities
        'explorer': {'bg': '#FFB900', 'fg': '#000000'},     # File Explorer Yellow
        'cmd': {'bg': '#0C0C0C', 'fg': '#FFFFFF'},          # Command Prompt Black
        'powershell': {'bg': '#012456', 'fg': '#FFFFFF'},   # PowerShell Blue
        'taskmgr': {'bg': '#0078D7', 'fg': '#FFFFFF'},      # Task Manager Blue
        'notepad': {'bg': '#D0D0D0', 'fg': '#000000'},      # Notepad Light Gray
        
        # Default
        'default': {'bg': '#6B6B6B', 'fg': '#FFFFFF'}       # Default Gray
    }
    
    @classmethod
    def get_app_colors(cls, process_name):
        """Get colors for an application based on process name"""
        # Remove .exe extension and convert to lowercase
        app_name = process_name.replace('.exe', '').lower()
        
        # Check for file extensions in the window title
        # This will be handled in the ManagedWindow class
        
        return cls.APP_COLORS.get(app_name, cls.APP_COLORS['default'])
    
    @classmethod
    def get_colors_for_file_type(cls, title):
        """Get colors based on file type in window title"""
        title_lower = title.lower()
        
        # Check for file types in title
        if '.xlsx' in title_lower or '.xls' in title_lower or '.csv' in title_lower:
            return cls.APP_COLORS['excel']
        elif '.docx' in title_lower or '.doc' in title_lower:
            return cls.APP_COLORS['winword']
        elif '.pptx' in title_lower or '.ppt' in title_lower:
            return cls.APP_COLORS['powerpnt']
        elif '.pdf' in title_lower:
            return cls.APP_COLORS['acrobat']
        elif '.accdb' in title_lower or '.mdb' in title_lower:
            return cls.APP_COLORS['msaccess']
        
        return None