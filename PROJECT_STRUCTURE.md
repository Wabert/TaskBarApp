# TaskbarApp Project Structure

## New Organized Structure

```
TaskbarApp/
├── main.py                    # Entry point (stays at root)
├── requirements.txt           # Dependencies (stays at root)
├── README.md                 # Documentation (stays at root)
├── logs/                     # Log files directory
│   └── taskbar_*.log
├── src/                      # All source code
│   ├── __init__.py
│   ├── core/                 # Core application modules
│   │   ├── __init__.py
│   │   ├── taskbar.py        # Main taskbar class
│   │   ├── config.py         # Configuration and constants
│   │   └── logger.py         # Logging configuration
│   ├── ui/                   # UI components
│   │   ├── __init__.py
│   │   ├── dialogs.py        # Dialog classes
│   │   ├── widgets.py        # Widget components
│   │   ├── filter_view.py    # FilterView component
│   │   ├── ui_components.py  # Compatibility layer
│   │   └── simple_window_factory.py
│   ├── features/             # Feature modules
│   │   ├── __init__.py
│   │   ├── window_management/
│   │   │   ├── __init__.py
│   │   │   ├── window_manager.py
│   │   │   ├── windows_menu.py
│   │   │   └── pinned_windows.py
│   │   ├── links/
│   │   │   ├── __init__.py
│   │   │   ├── links_manager.py
│   │   │   └── quick_links.py
│   │   ├── email/
│   │   │   ├── __init__.py
│   │   │   ├── email_manager.py
│   │   │   ├── email_menu.py
│   │   │   └── email_options_menu.py
│   │   ├── inventory/
│   │   │   ├── __init__.py
│   │   │   └── folder_inventory.py
│   │   └── snip/
│   │       ├── __init__.py
│   │       └── snip_feature.py
│   └── utils/                # Utility modules
│       ├── __init__.py
│       ├── utils.py          # General utilities
│       ├── explorer_utils.py # File explorer utilities
│       └── browse_choice_dialog.py
├── tests/                    # Unit tests
│   ├── __init__.py
│   ├── test_core/
│   ├── test_ui/
│   └── test_features/
├── docs/                     # Documentation
│   └── *.txt, *.xlsx files
└── venv/                     # Virtual environment

## File Movement Plan

### Core (src/core/)
- taskbar.py
- config.py
- logger.py

### UI (src/ui/)
- dialogs.py
- widgets.py
- filter_view.py
- ui_components.py
- simple_window_factory.py

### Features - Window Management (src/features/window_management/)
- window_manager.py
- windows_menu.py
- pinned_windows.py

### Features - Links (src/features/links/)
- links_manager.py
- quick_links.py

### Features - Email (src/features/email/)
- email_manager.py
- email_menu.py
- email_options_menu.py

### Features - Inventory (src/features/inventory/)
- folder_inventory.py

### Features - Snip (src/features/snip/)
- snip_feature.py

### Utils (src/utils/)
- utils.py
- explorer_utils.py
- browse_choice_dialog.py

### Files to keep at root
- main.py
- requirements.txt
- README.md
- code_exporter.py (utility script)
```