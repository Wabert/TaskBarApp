# main.py
"""
Main entry point for SuiteView Taskbar Application
"""
import sys
import os
import sys

print(sys.prefix)  # Shows venv path if active
print(sys.base_prefix)  # Shows original Python installation

# Am I in a venv?
in_venv = sys.prefix != sys.base_prefix

if in_venv:
    print("I am in a venv")
else:
    print("I am not in a venv") 

# Add the current directory to the Python path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
#print(f"Current directory: {current_dir}")

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

#print(f"sys.path: {sys.path}")

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