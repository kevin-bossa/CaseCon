import tkinter as tk
from tkinter import ttk
from textcore import transform_text, convert_clipboard_text, get_shortcuts, update_shortcut, get_setting, update_setting
import keyboard

# -------------------- Main Window --------------------
root = tk.Tk()
root.title("CaseCon")
root.geometry("460x500")
root.resizable(False, False)

# -------------------- Style Configuration --------------------
style = ttk.Style()
style.theme_use('default')
style.configure('TNotebook', borderwidth=0, relief='flat', background='#f0f0f0')
style.configure('TNotebook.Tab', borderwidth=0, relief='flat', background='#f0f0f0')
style.map('TNotebook.Tab', background=[('selected', '#f0f0f0'), ('active', '#e0e0e0')])

# -------------------- Notebook --------------------
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, columnspan=4, sticky="nsew")

tab_main = tk.Frame(notebook, bg='#f0f0f0')
notebook.add(tab_main, text="Main")

tab_settings = tk.Frame(notebook, bg='#f0f0f0')
notebook.add(tab_settings, text="Settings")

# -------------------- Settings Tab --------------------
settings_frame = tk.Frame(tab_settings, bg='#f0f0f0')
settings_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

def force_uppercase(P):
    return P == P.upper()

vcmd = (root.register(force_uppercase), "%P")

# Load current shortcuts from JSON
shortcuts = get_shortcuts()
entry_widgets = {}
row = 0
for mode, default in shortcuts.items():
    label_text = mode.capitalize() + ":"
    tk.Label(settings_frame, text=label_text, bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
    e = tk.Entry(settings_frame, width=35, validate="key", validatecommand=vcmd)
    # Display "NONE" for empty, unset, or invalid shortcuts
    e.insert(0, default.upper() if default and default.strip() and default.upper() != "NONE" else "NONE")
    e.grid(row=row, column=1, padx=(10, 0), pady=5)
    entry_widgets[mode] = e
    row += 1

# Checkboxes
start_with_windows_var = tk.IntVar(value=get_setting("start_with_windows"))
def on_start_with_windows_change():
    update_setting("start_with_windows", start_with_windows_var.get())
tk.Checkbutton(settings_frame, text="Start with Windows", variable=start_with_windows_var, command=on_start_with_windows_change, bg='#f0f0f0')\
    .grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 0))
row += 1

start_hidden_tray_var = tk.IntVar(value=get_setting("start_hidden_tray"))
def on_start_hidden_tray_change():
    update_setting("start_hidden_tray", start_hidden_tray_var.get())
tk.Checkbutton(settings_frame, text="Always start hidden in system tray", variable=start_hidden_tray_var, command=on_start_hidden_tray_change, bg='#f0f0f0')\
    .grid(row=row, column=0, columnspan=2, sticky="w", pady=(5, 0))

# -------------------- Dynamic Shortcut Management --------------------
dynamic_shortcuts = {mode: (default.upper() if default and default.strip() and default.upper() != "NONE" else "NONE") for mode, default in get_shortcuts().items()}
hotkey_handles = []

def register_hotkeys():
    """Unhook previous hotkeys and register current ones."""
    global hotkey_handles
    for handle in hotkey_handles:
        try:
            keyboard.remove_hotkey(handle)
        except (KeyError, ValueError):
            pass
    hotkey_handles = []

    print("Registering hotkeys:", dynamic_shortcuts)  # Debug: Log all shortcuts
    for mode, shortcut in dynamic_shortcuts.items():
        # Skip empty or invalid shortcuts
        if shortcut and shortcut.upper() != "NONE" and shortcut.strip():
            try:
                # Use lowercase for keyboard library registration
                handle = keyboard.add_hotkey(shortcut.lower(), lambda m=mode: convert_clipboard_text(m))
                hotkey_handles.append(handle)
                print(f"Registered hotkey: {mode} -> {shortcut.lower()}")  # Debug: Log successful registration
            except ValueError as e:
                print(f"Failed to register hotkey for {mode}: {shortcut} - {e}")  # Debug: Log errors
                continue
            except Exception as e:
                print(f"Unexpected error registering hotkey for {mode}: {shortcut} - {e}")  # Debug: Log unexpected errors
                continue

register_hotkeys()

# -------------------- Shortcut Recording --------------------
current_entry = None
previous_value = ""

def start_recording(entry):
    global current_entry, previous_value

    if current_entry:
        current_entry.delete(0, tk.END)
        current_entry.insert(0, previous_value)
        current_entry.config(bg='white', insertontime=600)
        keyboard.unhook_all()
        current_entry = None

    # Clear all existing hotkeys to prevent triggering during recording
    global hotkey_handles
    for handle in hotkey_handles:
        try:
            keyboard.remove_hotkey(handle)
        except (KeyError, ValueError):
            pass
    hotkey_handles = []

    previous_value = entry.get()
    current_entry = entry
    entry.delete(0, tk.END)
    entry.insert(0, "RECORD KEYS AND PRESS ENTER")
    entry.icursor(tk.END)
    entry.config(bg='#e8e8e8', insertontime=0)

    recorded_keys = []
    recording_finished = False

    def update_display():
        entry.delete(0, tk.END)
        if not recorded_keys:
            entry.insert(0, "RECORD KEYS AND PRESS ENTER")
        else:
            # Keep CTRL, SHIFT, ALT as modifiers
            modifiers = [k for k in recorded_keys if k in ['CTRL', 'SHIFT', 'ALT']]
            # All other keys except Caps Lock
            others = [k for k in recorded_keys if k not in ['CTRL', 'SHIFT', 'ALT', 'CAPSLOCK', 'MAYUSCULAS']]
            shortcut_text = '+'.join(modifiers + others).upper()
            entry.insert(0, shortcut_text)
        entry.icursor(tk.END)
        entry.update()  # Force UI refresh

    def on_key_event(event):
        nonlocal recording_finished
        if recording_finished or event.event_type != keyboard.KEY_DOWN:
            return False

        # Normalize key name
        key_name = event.name.upper()
        if key_name == 'MAYUSCULAS':
            key_name = 'SHIFT'  # Convert MAYUSCULAS to SHIFT

        if key_name == 'DELETE':
            recorded_keys.clear()
            update_display()
            return False
        if key_name == 'BACKSPACE':
            if recorded_keys:
                recorded_keys.pop()
                update_display()
            return False
        if key_name == 'ENTER':
            if not recording_finished:
                recording_finished = True
                keyboard.unhook_all()
                root.after(10, finish_recording)
            return False
        if key_name not in recorded_keys:
            recorded_keys.append(key_name)
            update_display()
        if len(recorded_keys) >= 4:
            recording_finished = True
            keyboard.unhook_all()
            root.after(10, finish_recording)
        return False

    def finish_recording():
        # Keep modifiers as proper keys
        modifiers = [k for k in recorded_keys if k in ['CTRL', 'SHIFT', 'ALT']]
        others = [k for k in recorded_keys if k not in ['CTRL', 'SHIFT', 'ALT', 'CAPSLOCK', 'MAYUSCULAS']]
        shortcut_text = '+'.join(modifiers + others).upper() if recorded_keys else "NONE"
        stop_recording(entry, shortcut_text)

    keyboard.hook(on_key_event)

def stop_recording(entry, shortcut_text):
    global current_entry, previous_value

    entry.delete(0, tk.END)
    entry.insert(0, shortcut_text.upper())
    entry.config(bg='white', insertontime=600)
    current_entry = None
    previous_value = ""

    mode = None
    for m, e in entry_widgets.items():
        if e == entry:
            mode = m
            break

    if mode:
        # Ensure empty shortcuts are saved as "NONE"
        update_shortcut(mode, shortcut_text.upper() if shortcut_text.strip() else "NONE")
        dynamic_shortcuts[mode] = shortcut_text.upper() if shortcut_text.strip() else "NONE"
        register_hotkeys()

    root.focus()

# Bind entries
for entry in entry_widgets.values():
    entry.bind("<Button-1>", lambda e, entry=entry: (start_recording(entry), "break"))
    entry.bind("<FocusIn>", lambda e, entry=entry: entry.icursor(tk.END))

notebook.bind("<<NotebookTabChanged>>", lambda e=None: root.focus())

# -------------------- Main Tab --------------------
main_frame = tk.Frame(tab_main, bg='#f0f0f0')
main_frame.grid(row=0, column=0, sticky="nsew")

buttons = [
    ("UPPERCASE", "uppercase"),
    ("lowercase", "lowercase"),
    ("Title Case", "titlecase"),
    ("Sentence\ncase", "sentencecase"),
    ("MACRO_CASE", "macrocase"),
    ("snake_case", "snakecase"),
    ("PascalCase", "pascalcase"),
    ("kebab-case", "kebabcase")
]

btn_widgets = []
for idx, (text, mode) in enumerate(buttons):
    r, c = divmod(idx, 4)
    btn = tk.Button(main_frame, text=text, height=2, width=10, font=("Courier New", 12),
                    command=lambda m=mode: convert(m))
    btn.grid(row=r, column=c, padx=(10 if c == 0 else 0, 0), pady=(10 if r == 0 else 0, 0))
    btn_widgets.append(btn)

status_label = tk.Label(main_frame, text="Words: 0 - Letters: 0 - All characters: 0",
                        bg='#f0f0f0', font=("Courier New", 10, "bold"))
status_label.grid(row=2, column=0, columnspan=4, padx=8, pady=(5, 0), sticky="w")

TextBox = tk.Text(main_frame, height=20, width=54)
TextBox.grid(row=3, column=0, columnspan=4, padx=(8,0), pady=(5,17))

def update_counts(event=None):
    content = TextBox.get("1.0", "end-1c")
    words = len(content.split())
    letters = sum(c.isalpha() for c in content)
    all_chars = len(content)
    status_label.config(text=f"Words: {words} - Letters: {letters} - All characters: {all_chars}")

TextBox.bind("<KeyRelease>", update_counts)
TextBox.bind("<<Paste>>", lambda e: root.after(10, update_counts))

def convert(mode):
    content = TextBox.get("1.0", "end-1c")
    result = transform_text(content, mode)
    TextBox.delete("1.0", "end")
    TextBox.insert("1.0", result)
    update_counts()

root.after(50, lambda: root.focus())
root.mainloop()