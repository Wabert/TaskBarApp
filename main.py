# main.py
"""
Main entry point for SuiteView Taskbar Application
"""
import sys
import os

# Add the current directory to the Python path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import our modules
try:
    from taskbar import SuiteViewTaskbar
    from config import Settings
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Files in directory: {os.listdir(current_dir)}")
    sys.exit(1)

def main():
    """Main application entry point"""
    try:
        print(f"Starting {Settings.APP_NAME} v{Settings.VERSION}")
        
        # Create and run the taskbar application
        app = SuiteViewTaskbar()
        app.run()
        
    except KeyboardInterrupt:
        print("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()