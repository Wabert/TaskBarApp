"""
UI Components for SuiteView Taskbar Application
This file now imports from separate modules for better organization
"""

# Import all components from their new locations
from .dialogs import (
    DialogBase,
    CustomDialog,
    ConfirmationDialog,
    LoadingDialog,
    WarningDialog,
    ErrorDialog,
    FilterMenuDialog
)

from .widgets import (
    FormField,
    CategoryHeader,
    SectionDivider,
    ScrollableFrame,
    ToolTip,
    ButtonFactory,
    UIUtils
)

from .filter_view import FilterView

# Re-export all components for backward compatibility
__all__ = [
    # Dialogs
    'DialogBase',
    'CustomDialog',
    'ConfirmationDialog',
    'LoadingDialog',
    'WarningDialog',
    'ErrorDialog',
    'FilterMenuDialog',
    
    # Widgets
    'FormField',
    'CategoryHeader',
    'SectionDivider',
    'ScrollableFrame',
    'ToolTip',
    'ButtonFactory',
    'UIUtils',
    
    # FilterView
    'FilterView'
]