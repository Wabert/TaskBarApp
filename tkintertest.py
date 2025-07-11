from tkinter import *
from tkinter import ttk

def calculate(*args):
    try:
        value = float(feet.get())
        meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
    except ValueError:
        pass

root = Tk()
root.title("Feet to Meters")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

feet = StringVar()
feet_entry = ttk.Entry(mainframe, width=17, textvariable=feet)
feet_entry.grid(column=2, row=1, sticky=(W, E))

meters = StringVar()
ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))

ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

ttk.Label(mainframe, text="test1").grid(column=4, row=4, sticky=W)
ttk.Label(mainframe, text="test2").grid(column=5, row=5, sticky=W)
ttk.Label(mainframe, text="test3").grid(column=6, row=6, sticky=W)

# Get the number of columns in the mainframe
columncount = mainframe.grid_size()[0]  # grid_size() returns (columns, rows)
rowcount = mainframe.grid_size()[1]

ttk.Label(mainframe, text=f"totalcolumns: {columncount}").grid(column=columncount, row=rowcount, sticky=W)
ttk.Label(mainframe, text=f"totalrows: {rowcount}").grid(column=columncount+1, row=rowcount+1, sticky=W)



for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

feet_entry.focus()
root.bind("<Return>", calculate)

root.mainloop()