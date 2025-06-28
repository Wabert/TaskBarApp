# inventory_view_examples.py
"""
Examples of using the reusable InventoryViewWindow pattern
Shows how to use it for different types of data throughout the SuiteView application
"""

from inventory_view_window import InventoryViewWindow
import tkinter as tk
from datetime import datetime, timedelta
import random

# Example 1: Email Attachments (as implemented)
def show_email_attachments(parent_window):
    """Example of showing email attachments"""
    # Sample email data
    email_data = [
        {
            'Date': '2025-06-28 10:30',
            'From': 'John Smith',
            'Subject': 'Q2 Financial Report',
            'Attachments': 'Q2_Report.pdf, Q2_Summary.xlsx',
            'AttachmentCount': 2,
            'EntryID': 'EMAIL001'
        },
        {
            'Date': '2025-06-27 14:15',
            'From': 'Mary Johnson',
            'Subject': 'Project Update - Screenshots',
            'Attachments': 'screenshot1.png, screenshot2.png, diagram.vsd',
            'AttachmentCount': 3,
            'EntryID': 'EMAIL002'
        }
    ]
    
    config = {
        'title': 'Email Attachments',
        'columns': [
            {'key': 'Date', 'header': 'Date', 'width': 120, 'type': 'date'},
            {'key': 'From', 'header': 'From', 'width': 200, 'type': 'text'},
            {'key': 'Subject', 'header': 'Subject', 'width': 300, 'type': 'text'},
            {'key': 'Attachments', 'header': 'Attachments', 'width': 250, 'type': 'text'},
            {'key': 'AttachmentCount', 'header': 'Count', 'width': 60, 'type': 'number'}
        ],
        'on_item_double_click': lambda item: print(f"Opening email: {item['Subject']}"),
        'window_width': 1100,
        'window_height': 600
    }
    
    InventoryViewWindow(parent_window, email_data, config)


# Example 2: Process Monitor
def show_process_monitor(parent_window):
    """Example of showing running processes"""
    # Sample process data
    process_data = [
        {
            'ProcessName': 'chrome.exe',
            'PID': 1234,
            'Memory': 512000000,  # bytes
            'CPU': 15.2,
            'Status': 'Running',
            'User': 'CurrentUser'
        },
        {
            'ProcessName': 'excel.exe',
            'PID': 5678,
            'Memory': 256000000,
            'CPU': 2.5,
            'Status': 'Running',
            'User': 'CurrentUser'
        }
    ]
    
    # Add formatted memory column
    for proc in process_data:
        proc['MemoryMB'] = f"{proc['Memory'] / (1024*1024):.1f} MB"
    
    config = {
        'title': 'Process Monitor',
        'columns': [
            {'key': 'ProcessName', 'header': 'Process', 'width': 150, 'type': 'text'},
            {'key': 'PID', 'header': 'PID', 'width': 80, 'type': 'number'},
            {'key': 'MemoryMB', 'header': 'Memory', 'width': 100, 'type': 'text'},
            {'key': 'CPU', 'header': 'CPU %', 'width': 80, 'type': 'number'},
            {'key': 'Status', 'header': 'Status', 'width': 100, 'type': 'text'},
            {'key': 'User', 'header': 'User', 'width': 120, 'type': 'text'}
        ],
        'on_item_double_click': lambda item: print(f"Process details: {item['ProcessName']}"),
        'window_width': 800,
        'window_height': 500,
        'additional_info': {
            'Total Processes': len(process_data),
            'Last Update': datetime.now().strftime('%H:%M:%S')
        }
    }
    
    InventoryViewWindow(parent_window, process_data, config)


# Example 3: Network Connections
def show_network_connections(parent_window):
    """Example of showing network connections"""
    connection_data = [
        {
            'LocalAddress': '192.168.1.100:443',
            'RemoteAddress': '142.250.80.46:80',
            'Protocol': 'TCP',
            'State': 'ESTABLISHED',
            'Process': 'chrome.exe',
            'BytesSent': 1024000,
            'BytesReceived': 5120000
        },
        {
            'LocalAddress': '192.168.1.100:1433',
            'RemoteAddress': '10.0.0.5:1433',
            'Protocol': 'TCP',
            'State': 'ESTABLISHED',
            'Process': 'sqlservr.exe',
            'BytesSent': 512000,
            'BytesReceived': 256000
        }
    ]
    
    config = {
        'title': 'Network Connections',
        'columns': [
            {'key': 'LocalAddress', 'header': 'Local Address', 'width': 150, 'type': 'text'},
            {'key': 'RemoteAddress', 'header': 'Remote Address', 'width': 150, 'type': 'text'},
            {'key': 'Protocol', 'header': 'Protocol', 'width': 80, 'type': 'text'},
            {'key': 'State', 'header': 'State', 'width': 120, 'type': 'text'},
            {'key': 'Process', 'header': 'Process', 'width': 120, 'type': 'text'},
            {'key': 'BytesSent', 'header': 'Sent', 'width': 100, 'type': 'number'},
            {'key': 'BytesReceived', 'header': 'Received', 'width': 100, 'type': 'number'}
        ],
        'window_width': 900,
        'window_height': 500
    }
    
    InventoryViewWindow(parent_window, connection_data, config)


# Example 4: Recent Documents
def show_recent_documents(parent_window):
    """Example of showing recent documents"""
    doc_data = [
        {
            'FileName': 'Budget_2025.xlsx',
            'Type': 'Excel',
            'Modified': '2025-06-28 09:15:00',
            'Size': 1048576,
            'Path': 'C:\\Documents\\Finance\\Budget_2025.xlsx',
            'Author': 'John Doe'
        },
        {
            'FileName': 'Presentation_Q2.pptx',
            'Type': 'PowerPoint',
            'Modified': '2025-06-27 16:30:00',
            'Size': 5242880,
            'Path': 'C:\\Documents\\Presentations\\Presentation_Q2.pptx',
            'Author': 'Jane Smith'
        }
    ]
    
    # Add formatted size
    for doc in doc_data:
        doc['SizeFormatted'] = f"{doc['Size'] / (1024*1024):.1f} MB"
    
    config = {
        'title': 'Recent Documents',
        'columns': [
            {'key': 'FileName', 'header': 'File Name', 'width': 200, 'type': 'text'},
            {'key': 'Type', 'header': 'Type', 'width': 100, 'type': 'text'},
            {'key': 'Modified', 'header': 'Last Modified', 'width': 150, 'type': 'date'},
            {'key': 'SizeFormatted', 'header': 'Size', 'width': 80, 'type': 'text'},
            {'key': 'Author', 'header': 'Author', 'width': 120, 'type': 'text'},
            {'key': 'Path', 'header': 'Location', 'width': 300, 'type': 'text'}
        ],
        'on_item_double_click': lambda item: print(f"Opening: {item['Path']}"),
        'window_width': 1000,
        'window_height': 500
    }
    
    InventoryViewWindow(parent_window, doc_data, config)


# Example 5: Task List / To-Do Items
def show_task_list(parent_window):
    """Example of showing a task list"""
    task_data = [
        {
            'TaskID': 1,
            'Title': 'Complete quarterly report',
            'Priority': 'High',
            'Status': 'In Progress',
            'DueDate': '2025-06-30',
            'AssignedTo': 'John Doe',
            'Category': 'Finance',
            'Progress': 75
        },
        {
            'TaskID': 2,
            'Title': 'Review budget proposals',
            'Priority': 'Medium',
            'Status': 'Not Started',
            'DueDate': '2025-07-05',
            'AssignedTo': 'Jane Smith',
            'Category': 'Finance',
            'Progress': 0
        }
    ]
    
    config = {
        'title': 'Task Management',
        'columns': [
            {'key': 'TaskID', 'header': 'ID', 'width': 50, 'type': 'number'},
            {'key': 'Title', 'header': 'Task', 'width': 250, 'type': 'text'},
            {'key': 'Priority', 'header': 'Priority', 'width': 80, 'type': 'text'},
            {'key': 'Status', 'header': 'Status', 'width': 100, 'type': 'text'},
            {'key': 'DueDate', 'header': 'Due Date', 'width': 100, 'type': 'date'},
            {'key': 'AssignedTo', 'header': 'Assigned To', 'width': 120, 'type': 'text'},
            {'key': 'Category', 'header': 'Category', 'width': 100, 'type': 'text'},
            {'key': 'Progress', 'header': 'Progress %', 'width': 80, 'type': 'number'}
        ],
        'on_item_double_click': lambda item: print(f"Edit task: {item['Title']}"),
        'window_width': 900,
        'window_height': 500,
        'additional_info': {
            'Total Tasks': len(task_data),
            'High Priority': len([t for t in task_data if t['Priority'] == 'High'])
        }
    }
    
    InventoryViewWindow(parent_window, task_data, config)


# Example 6: Using auto-generated columns (no configuration)
def show_auto_columns(parent_window):
    """Example of using auto-generated columns"""
    # Simple data - columns will be auto-generated
    simple_data = [
        {
            'name': 'Item 1',
            'value': 100,
            'date_created': '2025-06-28',
            'active': 'Yes'
        },
        {
            'name': 'Item 2',
            'value': 200,
            'date_created': '2025-06-27',
            'active': 'No'
        }
    ]
    
    # Minimal configuration - columns will be auto-generated
    config = {
        'title': 'Auto-Generated Columns Example',
        'window_width': 600,
        'window_height': 400
    }
    
    InventoryViewWindow(parent_window, simple_data, config)


# Test function to demonstrate all examples
def test_inventory_views():
    """Test function to demonstrate all inventory view examples"""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Create a simple menu to launch different examples
    menu_window = tk.Toplevel(root)
    menu_window.title("Inventory View Examples")
    menu_window.geometry("300x400")
    
    examples = [
        ("Email Attachments", show_email_attachments),
        ("Process Monitor", show_process_monitor),
        ("Network Connections", show_network_connections),
        ("Recent Documents", show_recent_documents),
        ("Task List", show_task_list),
        ("Auto Columns", show_auto_columns)
    ]
    
    tk.Label(menu_window, text="Click to view examples:", font=('Arial', 12, 'bold')).pack(pady=10)
    
    for title, func in examples:
        btn = tk.Button(menu_window, text=title, width=25,
                       command=lambda f=func: f(root))
        btn.pack(pady=5)
    
    tk.Button(menu_window, text="Exit", width=25, command=root.quit).pack(pady=20)
    
    root.mainloop()


if __name__ == "__main__":
    test_inventory_views()