# SuiteView Taskbar App

A simple, customizable taskbar app for Windows 11, built with PySide2.

## Features
- Always-on-top, borderless taskbar bar
- Two-tone green theme
- System tray integration
- Easy to extend with new buttons and features

## Setup
1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python main.py
   ```

## Packaging (Optional)
To create a standalone executable, install PyInstaller:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## Customization
- Add new buttons and features by editing `main.py`.
- Update colors and styles in the code as desired. 