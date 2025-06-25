import ctypes
from ctypes import wintypes
import time

def fix_desktop_space():
    """Force restore desktop working area"""
    user32 = ctypes.windll.user32
    
    # Method 1: Get actual screen size and restore
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    
    print(f"Screen size: {screen_width}x{screen_height}")
    
    # Method 2: Force full screen work area
    full_area = wintypes.RECT(0, 0, screen_width, screen_height)
    result = user32.SystemParametersInfoW(0x002F, 0, ctypes.byref(full_area), 0)
    print(f"Full restore attempt: {'Success' if result else 'Failed'}")
    
    # Method 3: Broadcast change to all windows
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 0)
    
    # Method 4: Try with SPIF_SENDCHANGE flag
    SPIF_SENDCHANGE = 0x0002
    SPIF_UPDATEINIFILE = 0x0001
    result2 = user32.SystemParametersInfoW(0x002F, 0, ctypes.byref(full_area), SPIF_SENDCHANGE | SPIF_UPDATEINIFILE)
    print(f"Restore with flags: {'Success' if result2 else 'Failed'}")
    
    # Method 5: Explorer restart (most aggressive)
    print("\nRestarting Explorer to force refresh...")
    import os
    os.system("taskkill /f /im explorer.exe")
    time.sleep(1)
    os.system("start explorer.exe")

if __name__ == "__main__":
    fix_desktop_space()
    print("\nDesktop space should be restored!")
    print("If not, try logging out and back in.")