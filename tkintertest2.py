import tkinter as tk
from tkinter import ttk
import sys

class TTKStyleDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("TTK Styles Demonstration")
        self.root.geometry("800x600")
        
        # Create style object
        self.style = ttk.Style()
        
        # Create main notebook for different sections
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create different tabs
        self.create_themes_tab()
        self.create_widgets_tab()
        self.create_custom_styles_tab()
        
    def create_themes_tab(self):
        """Tab showing different built-in themes"""
        themes_frame = ttk.Frame(self.notebook)
        self.notebook.add(themes_frame, text="Built-in Themes")
        
        # Theme selection
        ttk.Label(themes_frame, text="Select Theme:", font=("Arial", 12, "bold")).pack(pady=10)
        
        theme_var = tk.StringVar(value=self.style.theme_use())
        theme_combo = ttk.Combobox(themes_frame, textvariable=theme_var, 
                                  values=self.style.theme_names(), state="readonly")
        theme_combo.pack(pady=5)
        theme_combo.bind('<<ComboboxSelected>>', lambda e: self.change_theme(theme_var.get()))
        
        # Sample widgets to show theme differences
        sample_frame = ttk.LabelFrame(themes_frame, text="Sample Widgets", padding=20)
        sample_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Row 1: Buttons
        button_frame = ttk.Frame(sample_frame)
        button_frame.pack(fill="x", pady=5)
        ttk.Label(button_frame, text="Buttons:").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Normal Button").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Disabled", state="disabled").pack(side="left", padx=5)
        
        # Row 2: Entry and Combobox
        entry_frame = ttk.Frame(sample_frame)
        entry_frame.pack(fill="x", pady=5)
        ttk.Label(entry_frame, text="Entry:").pack(side="left", padx=5)
        entry = ttk.Entry(entry_frame, width=20)
        entry.pack(side="left", padx=5)
        entry.insert(0, "Sample text")
        
        ttk.Label(entry_frame, text="Combobox:").pack(side="left", padx=10)
        combo = ttk.Combobox(entry_frame, values=["Option 1", "Option 2", "Option 3"], width=15)
        combo.pack(side="left", padx=5)
        combo.set("Option 1")
        
        # Row 3: Checkbutton and Radiobutton
        check_frame = ttk.Frame(sample_frame)
        check_frame.pack(fill="x", pady=5)
        ttk.Label(check_frame, text="Checkboxes:").pack(side="left", padx=5)
        
        check_var1 = tk.BooleanVar(value=True)
        check_var2 = tk.BooleanVar()
        ttk.Checkbutton(check_frame, text="Option 1", variable=check_var1).pack(side="left", padx=5)
        ttk.Checkbutton(check_frame, text="Option 2", variable=check_var2).pack(side="left", padx=5)
        
        # Row 4: Scale and Progressbar
        scale_frame = ttk.Frame(sample_frame)
        scale_frame.pack(fill="x", pady=5)
        ttk.Label(scale_frame, text="Scale:").pack(side="left", padx=5)
        ttk.Scale(scale_frame, from_=0, to=100, length=150).pack(side="left", padx=5)
        
        ttk.Label(scale_frame, text="Progress:").pack(side="left", padx=10)
        progress = ttk.Progressbar(scale_frame, length=150, mode='determinate')
        progress.pack(side="left", padx=5)
        progress['value'] = 60
        
    def create_widgets_tab(self):
        """Tab showing all available widget styles"""
        widgets_frame = ttk.Frame(self.notebook)
        self.notebook.add(widgets_frame, text="Widget Styles")
        
        # Create scrollable frame
        canvas = tk.Canvas(widgets_frame)
        scrollbar = ttk.Scrollbar(widgets_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Widget demonstrations
        row = 0
        
        # Buttons
        ttk.Label(scrollable_frame, text="BUTTONS", font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=3, sticky="w", pady=(10,5))
        row += 1
        
        ttk.Label(scrollable_frame, text="TButton:").grid(row=row, column=0, sticky="w", padx=5)
        ttk.Button(scrollable_frame, text="Standard Button").grid(row=row, column=1, padx=5, pady=2)
        ttk.Label(scrollable_frame, text="Default button style").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="Toolbutton:").grid(row=row, column=0, sticky="w", padx=5)
        ttk.Button(scrollable_frame, text="Tool Button", style="Toolbutton").grid(row=row, column=1, padx=5, pady=2)
        ttk.Label(scrollable_frame, text="Flat toolbar-style button").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        # Labels and Entry
        ttk.Label(scrollable_frame, text="LABELS & ENTRY", font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=3, sticky="w", pady=(10,5))
        row += 1
        
        ttk.Label(scrollable_frame, text="TLabel:").grid(row=row, column=0, sticky="w", padx=5)
        ttk.Label(scrollable_frame, text="Standard Label").grid(row=row, column=1, padx=5, pady=2)
        ttk.Label(scrollable_frame, text="Default label style").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="TEntry:").grid(row=row, column=0, sticky="w", padx=5)
        entry = ttk.Entry(scrollable_frame, width=15)
        entry.grid(row=row, column=1, padx=5, pady=2, sticky="w")
        entry.insert(0, "Text input")
        ttk.Label(scrollable_frame, text="Text entry field").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        # Selection widgets
        ttk.Label(scrollable_frame, text="SELECTION WIDGETS", font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=3, sticky="w", pady=(10,5))
        row += 1
        
        ttk.Label(scrollable_frame, text="TCheckbutton:").grid(row=row, column=0, sticky="w", padx=5)
        check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(scrollable_frame, text="Checkbox", variable=check_var).grid(row=row, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(scrollable_frame, text="Checkbox control").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="TRadiobutton:").grid(row=row, column=0, sticky="w", padx=5)
        radio_var = tk.StringVar(value="option1")
        ttk.Radiobutton(scrollable_frame, text="Radio", variable=radio_var, value="option1").grid(row=row, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(scrollable_frame, text="Radio button control").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="TCombobox:").grid(row=row, column=0, sticky="w", padx=5)
        combo = ttk.Combobox(scrollable_frame, values=["Item 1", "Item 2", "Item 3"], width=12)
        combo.grid(row=row, column=1, padx=5, pady=2, sticky="w")
        combo.set("Item 1")
        ttk.Label(scrollable_frame, text="Dropdown selection").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        # Display widgets
        ttk.Label(scrollable_frame, text="DISPLAY WIDGETS", font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=3, sticky="w", pady=(10,5))
        row += 1
        
        ttk.Label(scrollable_frame, text="TProgressbar:").grid(row=row, column=0, sticky="w", padx=5)
        progress = ttk.Progressbar(scrollable_frame, length=120, mode='determinate')
        progress.grid(row=row, column=1, padx=5, pady=2, sticky="w")
        progress['value'] = 40
        ttk.Label(scrollable_frame, text="Progress indicator").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="TScale:").grid(row=row, column=0, sticky="w", padx=5)
        ttk.Scale(scrollable_frame, from_=0, to=100, length=120).grid(row=row, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(scrollable_frame, text="Slider control").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        # Container widgets
        ttk.Label(scrollable_frame, text="CONTAINERS", font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=3, sticky="w", pady=(10,5))
        row += 1
        
        ttk.Label(scrollable_frame, text="TFrame:").grid(row=row, column=0, sticky="w", padx=5)
        frame_demo = ttk.Frame(scrollable_frame, relief="solid", borderwidth=1)
        frame_demo.grid(row=row, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(frame_demo, text="Frame").pack(padx=5, pady=2)
        ttk.Label(scrollable_frame, text="Container frame").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="TLabelframe:").grid(row=row, column=0, sticky="w", padx=5)
        labelframe_demo = ttk.LabelFrame(scrollable_frame, text="Group", padding=5)
        labelframe_demo.grid(row=row, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(labelframe_demo, text="Content").pack()
        ttk.Label(scrollable_frame, text="Labeled frame").grid(row=row, column=2, sticky="w", padx=5)
        row += 1
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_custom_styles_tab(self):
        """Tab showing custom style examples"""
        custom_frame = ttk.Frame(self.notebook)
        self.notebook.add(custom_frame, text="Custom Styles")
        
        ttk.Label(custom_frame, text="Custom Style Examples", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        # Create custom styles
        self.create_custom_styles()
        
        # Demo frame
        demo_frame = ttk.LabelFrame(custom_frame, text="Custom Styled Widgets", padding=20)
        demo_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Custom buttons
        button_frame = ttk.Frame(demo_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Label(button_frame, text="Custom Buttons:", font=("Arial", 12, "bold")).pack(anchor="w")
        
        buttons_container = ttk.Frame(button_frame)
        buttons_container.pack(fill="x", pady=5)
        
        ttk.Button(buttons_container, text="Success", style="Success.TButton").pack(side="left", padx=5)
        ttk.Button(buttons_container, text="Warning", style="Warning.TButton").pack(side="left", padx=5)
        ttk.Button(buttons_container, text="Danger", style="Danger.TButton").pack(side="left", padx=5)
        ttk.Button(buttons_container, text="Info", style="Info.TButton").pack(side="left", padx=5)
        
        # Custom labels
        label_frame = ttk.Frame(demo_frame)
        label_frame.pack(fill="x", pady=10)
        
        ttk.Label(label_frame, text="Custom Labels:", font=("Arial", 12, "bold")).pack(anchor="w")
        
        labels_container = ttk.Frame(label_frame)
        labels_container.pack(fill="x", pady=5)
        
        ttk.Label(labels_container, text="Header Text", style="Header.TLabel").pack(anchor="w")
        ttk.Label(labels_container, text="Subheader Text", style="Subheader.TLabel").pack(anchor="w")
        ttk.Label(labels_container, text="Highlighted Text", style="Highlight.TLabel").pack(anchor="w")
        
        # Custom entry
        entry_frame = ttk.Frame(demo_frame)
        entry_frame.pack(fill="x", pady=10)
        
        ttk.Label(entry_frame, text="Custom Entry:", font=("Arial", 12, "bold")).pack(anchor="w")
        
        entry_container = ttk.Frame(entry_frame)
        entry_container.pack(fill="x", pady=5)
        
        custom_entry = ttk.Entry(entry_container, style="Custom.TEntry", width=30)
        custom_entry.pack(side="left", padx=5)
        custom_entry.insert(0, "Custom styled entry")
        
        # Style code example
        code_frame = ttk.LabelFrame(demo_frame, text="Style Code Example", padding=10)
        code_frame.pack(fill="both", expand=True, pady=10)
        
        code_text = '''# Creating custom styles:
style = ttk.Style()

# Success button (green)
style.configure('Success.TButton', 
                background='#28a745',
                foreground='white',
                font=('Arial', 10, 'bold'))

# Warning button (orange)  
style.configure('Warning.TButton',
                background='#ffc107', 
                foreground='black',
                font=('Arial', 10, 'bold'))

# Custom entry with different colors
style.configure('Custom.TEntry',
                fieldbackground='#f8f9fa',
                borderwidth=2,
                relief='solid')'''
        
        text_widget = tk.Text(code_frame, height=15, font=("Courier", 9))
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", code_text)
        text_widget.configure(state="disabled")
        
    def create_custom_styles(self):
        """Create custom styles for demonstration"""
        # Custom button styles
        self.style.configure('Success.TButton',
                           background='#28a745',
                           foreground='white',
                           font=('Arial', 10, 'bold'))
        
        self.style.configure('Warning.TButton',
                           background='#ffc107',
                           foreground='black', 
                           font=('Arial', 10, 'bold'))
        
        self.style.configure('Danger.TButton',
                           background='#dc3545',
                           foreground='white',
                           font=('Arial', 10, 'bold'))
        
        self.style.configure('Info.TButton',
                           background='#17a2b8',
                           foreground='white',
                           font=('Arial', 10, 'bold'))
        
        # Custom label styles
        self.style.configure('Header.TLabel',
                           font=('Arial', 16, 'bold'),
                           foreground='#2c3e50')
        
        self.style.configure('Subheader.TLabel',
                           font=('Arial', 12, 'bold'),
                           foreground='#34495e')
        
        self.style.configure('Highlight.TLabel',
                           font=('Arial', 10),
                           foreground='#e74c3c',
                           background='#fff3cd')
        
        # Custom entry style
        self.style.configure('Custom.TEntry',
                           fieldbackground='#f8f9fa',
                           borderwidth=2,
                           relief='solid')
        
    def change_theme(self, theme_name):
        """Change the current theme"""
        try:
            self.style.theme_use(theme_name)
            # Recreate custom styles after theme change
            self.create_custom_styles()
        except tk.TclError:
            pass

def main():
    root = tk.Tk()
    app = TTKStyleDemo(root)
    root.mainloop()

if __name__ == "__main__":
    main()