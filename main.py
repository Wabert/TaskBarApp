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
    from src.core import SuiteViewTaskbar, Settings, LoggingConfig, setup_logging, get_logger
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Files in directory: {os.listdir(current_dir)}")
    sys.exit(1)

def main():
    """Main application entry point"""
    # Initialize logging
    setup_logging()
    logger = get_logger('main')
    
    try:
        logger.info(f"Starting {Settings.APP_NAME} v{Settings.VERSION}")
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"Working directory: {os.getcwd()}")
        
        # Create and run the taskbar application
        app = SuiteViewTaskbar()
        logger.info("TaskbarApp initialized successfully")
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()