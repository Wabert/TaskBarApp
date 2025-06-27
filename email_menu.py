import tkinter as tk
from config import Colors, Fonts
from email_manager import EmailManager
from inventory_view_window import InventoryViewWindow
import win32com.client

class EmailMenu(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg=Colors.DARK_GREEN)
        self.attributes('-topmost', True)
        self.geometry("600x400")  # Adjusted size for better layout
        # Remove window title bar
        self.overrideredirect(True)

        # Initialize EmailManager
        self.email_manager = EmailManager()

        # Create main frame
        self.main_frame = tk.Frame(self, bg=Colors.DARK_GREEN)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create header with close button
        self.create_header()

        # Create scrollable content area
        self.create_scrollable_content()

        # Fetch and display emails
        self.display_emails()

        # Make the menu resizable
        self.create_resize_handles()

    def create_header(self):
        header_frame = tk.Frame(self.main_frame, bg=Colors.DARK_GREEN, height=30)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Title label
        title_label = tk.Label(header_frame, text="Email Attachments", bg=Colors.DARK_GREEN, fg=Colors.WHITE, font=Fonts.TASKBAR_TITLE)
        title_label.pack(side=tk.LEFT, padx=10)

        # Close button
        close_btn = tk.Button(header_frame, text="X", bg=Colors.MEDIUM_GREEN, fg=Colors.BLACK, font=Fonts.TASKBAR_BUTTON, command=self.close_menu)
        close_btn.pack(side=tk.RIGHT, padx=10)

        # Bind drag events to the header
        header_frame.bind("<Button-1>", self.start_drag)
        header_frame.bind("<B1-Motion>", self.do_drag)

    def create_scrollable_content(self):
        self.content_frame = tk.Frame(self.main_frame, bg=Colors.LIGHT_GREEN)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.content_frame, bg=Colors.LIGHT_GREEN, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.LIGHT_GREEN)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def display_emails(self):
        emails = self.email_manager.get_emails_with_attachments()
        email_data = [
            {
                'Date': email['Date'],
                'From': email['From'],
                'Subject': email['Subject'],
                'webLink': email['webLink']
            }
            for email in emails
        ]
        self.show_email_inventory(email_data)

    def show_email_inventory(self, email_data):
        scan_info = {
            'folder': 'Emails',
            'generated': 'N/A',
            'total_items': len(email_data),
            'max_depth': 'N/A',
            'content_type': 'Emails'
        }
        display_columns = ["Date", "From", "Subject"]
        display_column_widths = {'Date': 100,'From': 300,'Subject': 400,}
        InventoryViewWindow(self, email_data, [], scan_info,display_columns , display_column_widths)

    def open_email(self, email):
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail_item = outlook.Session.GetItemFromID(email['webLink'])
        mail_item.Display()

    def close_menu(self):
        self.destroy()

    def start_drag(self, event):
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def do_drag(self, event):
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y
        new_x = self.winfo_x() + dx
        new_y = self.winfo_y() + dy
        self.geometry(f"+{new_x}+{new_y}")
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def create_resize_handles(self):
        # Top resize handle
        top_handle = tk.Frame(self, cursor='size_ns', height=5)
        top_handle.place(relx=0.0, rely=0.0, relwidth=1.0, anchor='nw')
        top_handle.configure(bg=Colors.DARK_GREEN)

        # Left resize handle
        left_handle = tk.Frame(self, cursor='size_we', width=5)
        left_handle.place(relx=0.0, rely=0.0, relheight=1.0, anchor='nw')
        left_handle.configure(bg=Colors.DARK_GREEN)

        # Right resize handle
        right_handle = tk.Frame(self, cursor='size_we', width=5)
        right_handle.place(relx=1.0, rely=0.0, relheight=1.0, anchor='ne')
        right_handle.configure(bg=Colors.DARK_GREEN)

        # Bind resize events
        top_handle.bind("<Button-1>", lambda e: self.start_resize(e, 't'))
        top_handle.bind("<B1-Motion>", self.do_resize)
        top_handle.bind("<ButtonRelease-1>", self.end_resize)

        left_handle.bind("<Button-1>", lambda e: self.start_resize(e, 'l'))
        left_handle.bind("<B1-Motion>", self.do_resize)
        left_handle.bind("<ButtonRelease-1>", self.end_resize)

        right_handle.bind("<Button-1>", lambda e: self.start_resize(e, 'r'))
        right_handle.bind("<B1-Motion>", self.do_resize)
        right_handle.bind("<ButtonRelease-1>", self.end_resize)

    def start_resize(self, event, edge):
        self.is_resizing = True
        self.resize_edge = edge
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.original_geometry = {
            'x': self.winfo_x(),
            'y': self.winfo_y(),
            'width': self.winfo_width(),
            'height': self.winfo_height()
        }

    def do_resize(self, event):
        if not self.is_resizing or not self.resize_edge:
            return

        dx = event.x_root - self.resize_start_x
        dy = event.y_root - self.resize_start_y

        x = self.original_geometry['x']
        y = self.original_geometry['y']
        width = self.original_geometry['width']
        height = self.original_geometry['height']

        min_width = 300
        min_height = 200

        if self.resize_edge == 't':  # Top edge
            new_height = max(min_height, height - dy)
            if new_height != height:
                y = y + (height - new_height)
                height = new_height

        elif self.resize_edge == 'l':  # Left edge
            new_width = max(min_width, width - dx)
            if new_width != width:
                x = x + (width - new_width)
                width = new_width

        elif self.resize_edge == 'r':  # Right edge
            new_width = max(min_width, width + dx)
            width = new_width

        self.geometry(f"{int(width)}x{int(height)}+{int(x)}+{int(y)}")

    def end_resize(self, event):
        self.is_resizing = False
        self.resize_edge = None
