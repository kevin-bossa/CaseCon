import tkinter as tk
from main import transform_text

# Creating the main window
root = tk.Tk()
root.title("AnyCase-Clone")
root.geometry("300x200")

# Creating the text box
TextBox = tk.Text(root, height=10, width=30)

# Getting the text
def convert(mode):
    content = TextBox.get("1.0", "end-1c")
    result = transform_text(content, mode)
    TextBox.delete("1.0", "end")
    TextBox.insert("1.0", result)

# Creating the buttons and configuring them
UpperCase = tk.Button(root, text="UPPERCASE", height=2, font=("Courier New", 12))
LowerCase = tk.Button(root, text="lowercase", height=2, font=("Courier New", 12))
UpperCase.config(command=lambda: convert("uppercase"))
LowerCase.config(command=lambda : convert("lowercase"))

# Widgets positions
UpperCase.grid(row=0,column=0,padx=10,pady=10)
LowerCase.grid(row=0,column=1,padx=0,pady=10)
TextBox.grid(row=1,column=0, columnspan=2, padx=10,pady=10)

# Starts the main loop
root.mainloop()