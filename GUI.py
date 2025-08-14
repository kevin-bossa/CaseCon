import tkinter as tk
from main import transform_text

# Creating the main window
root = tk.Tk()
root.title("AnyCase-Clone")
root.geometry("460x500")
root.resizable(False,False)

# Creating the text box
TextBox = tk.Text(root, height=22, width=54)

# Getting the text
def convert(mode):
    content = TextBox.get("1.0", "end-1c")
    result = transform_text(content, mode)
    TextBox.delete("1.0", "end")
    TextBox.insert("1.0", result)

# Creating the buttons
UpperCase = tk.Button(root, text="UPPERCASE", height=2, width=10, font=("Courier New", 12))
LowerCase = tk.Button(root, text="lowercase", height=2, width=10, font=("Courier New", 12))
TitleCase = tk.Button(root, text="Title Case", height=2, width=10, font=("Courier New", 12))
SentenceCase = tk.Button(root, text="Sentence\ncase", height=2, width=10, font=("Courier New", 12))
MacroCase = tk.Button(root, text="MACRO_CASE", height=2, width=10, font=("Courier New", 12))
SnakeCase = tk.Button(root, text="snake_case", height=2, width=10, font=("Courier New", 12))
PascalCase = tk.Button(root, text="PascalCase", height=2, width=10, font=("Courier New", 12))
KebabCase = tk.Button(root, text="kebak-case", height=2, width=10, font=("Courier New", 12))

# Configuring the buttons
UpperCase.config(command=lambda: convert("uppercase"))
LowerCase.config(command=lambda : convert("lowercase"))
TitleCase.config(command=lambda: convert("titlecase"))
SentenceCase.config(command=lambda: convert("sentencecase"))
MacroCase.config(command=lambda: convert("macrocase"))
SnakeCase.config(command=lambda: convert("snakecase"))
PascalCase.config(command=lambda: convert("pascalcase"))
KebabCase.config(command=lambda: convert("kebabcase"))

# Widgets positions
UpperCase.grid(row=0,column=0,padx=(10,0),pady=(10,0))
LowerCase.grid(row=0,column=1,padx=0,pady=(10,0))
TitleCase.grid(row=0,column=2,padx=0,pady=(10,0))
SentenceCase.grid(row=0,column=3,padx=0,pady=(10,0))
MacroCase.grid(row=1,column=0,padx=(10,0),pady=0)
SnakeCase.grid(row=1,column=1,padx=0,pady=0)
PascalCase.grid(row=1,column=2,padx=0,pady=0)
KebabCase.grid(row=1,column=3,padx=0,pady=0)
TextBox.grid(row=3,column=0, columnspan=4, padx=(8,0),pady=17)

# Starts the main loop
root.mainloop()