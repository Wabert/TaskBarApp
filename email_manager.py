import win32com.client
from datetime import datetime, timedelta
from inventory_view_window import InventoryViewWindow
import tkinter as tk

class EmailManager:
    def __init__(self):
        self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        self.root = tk.Tk()

    def get_emails_with_attachments(self):
        inbox = self.outlook.GetDefaultFolder(6)  # 6 refers to the inbox
        messages = inbox.Items
        messages = messages.Restrict("[ReceivedTime] >= '" + (datetime.now() - timedelta(weeks=2)).strftime("%m/%d/%Y %H:%M %p") + "'")
        emails_with_attachments = []
        for message in messages:
            if message.Attachments.Count > 0:
                emails_with_attachments.append({
                    'Date': message.ReceivedTime.strftime("%m/%d/%Y %H:%M %p"),
                    'From': message.SenderName,
                    'Subject': message.Subject,
                    'webLink': message.EntryID  # Use EntryID to open the email
                })
        return emails_with_attachments
    
    def display_emails(self):
        emails = self.get_emails_with_attachments()
        email_data = [
            {
                'Date': email['Date'],
                'From': email['From'],
                'Subject': email['Subject'],
                'webLink': email['webLink']
            }
            for email in emails
        ]
        
        scan_info = {
            'folder': 'Emails',
            'generated': 'N/A',
            'total_items': len(email_data),
            'max_depth': 'N/A',
            'content_type': 'Emails'
        }
        display_columns = ["Date", "From", "Subject"]
        display_column_widths = {'Date': 100,'From': 300,'Subject': 400,}
        InventoryViewWindow(self.root, email_data, [], scan_info, display_columns , display_column_widths)