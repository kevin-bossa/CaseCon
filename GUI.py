import tkinter as tk
from tkinter import ttk
import keyboard
import pystray
from PIL import Image, ImageDraw
import threading
import sys
import winreg
import os

# Change to script directory to ensure relative imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add error logging for startup debugging
import traceback
import datetime

def log_error(error_msg):
    """Log errors to a file for debugging startup issues"""
    try:
        with open("casecon_error.log", "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {error_msg}\n")
    except:
        pass

try:
    from textcore import transform_text, convert_clipboard_text, get_shortcuts, update_shortcut, get_setting, update_setting
except Exception as e:
    error_msg = f"Failed to import textcore: {str(e)}\n{traceback.format_exc()}"
    log_error(error_msg)
    print(error_msg)
    sys.exit(1)

# -------------------- Windows Startup Management --------------------
def add_to_startup():
    """Add the application to Windows startup"""
    try:
        # Get the path to the current script
        app_path = os.path.abspath(sys.argv[0])
        script_dir = os.path.dirname(app_path)
        
        # Create a batch file for reliable startup
        batch_path = os.path.join(script_dir, "start_casecon.bat")
        python_path = sys.executable
        
        # Use pythonw.exe instead of python.exe to run without console window
        pythonw_path = python_path.replace('python.exe', 'pythonw.exe')
        
        batch_content = f'''@echo off
cd /d "{script_dir}"
"{pythonw_path}" "{app_path}"
'''
        
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        # Open the Windows registry key for startup programs
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_SET_VALUE)
        
        # Add the batch file to startup
        winreg.SetValueEx(key, "CaseCon", 0, winreg.REG_SZ, f'"{batch_path}"')
        winreg.CloseKey(key)
        print(f"Added to Windows startup via batch file: {batch_path}")
    except Exception as e:
        print(f"Failed to add to startup: {e}")
        log_error(f"Failed to add to startup: {str(e)}\n{traceback.format_exc()}")

def remove_from_startup():
    """Remove the application from Windows startup"""
    try:
        # Remove the batch file if it exists
        script_dir = os.path.dirname(os.path.abspath(__file__))
        batch_path = os.path.join(script_dir, "start_casecon.bat")
        if os.path.exists(batch_path):
            os.remove(batch_path)
        
        # Open the Windows registry key for startup programs
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_SET_VALUE)
        
        # Remove our application from startup
        winreg.DeleteValue(key, "CaseCon")
        winreg.CloseKey(key)
        print("Removed from Windows startup")
    except FileNotFoundError:
        # Entry doesn't exist, which is fine
        print("Startup entry not found (already removed)")
    except Exception as e:
        print(f"Failed to remove from startup: {e}")
        log_error(f"Failed to remove from startup: {str(e)}\n{traceback.format_exc()}")

def is_in_startup():
    """Check if the application is currently set to start with Windows"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "CaseCon")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

# -------------------- System Tray Setup --------------------
def create_tray_icon():
    """Create a tray icon using the same icon file as the window"""
    try:
        # Try to use the same icon file for the tray
        icon_path = os.path.join(script_dir, "icon.ico")
        if os.path.exists(icon_path):
            # Convert ICO to PIL Image for the tray icon
            image = Image.open(icon_path)
            return image
        else:
            # Fallback to creating a simple icon
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.rectangle([16, 16, 48, 48], fill='white')
            draw.text((20, 28), "CC", fill='black')
            return image
    except Exception as e:
        print(f"Failed to load icon for tray: {e}")
        # Fallback to creating a simple icon
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')
        draw.text((20, 28), "CC", fill='black')
        return image

def show_window():
    """Show the main window"""
    root.deiconify()
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    # Switch back to the main tab when restoring from tray
    notebook.select(tab_main)

def hide_window():
    """Hide the main window"""
    root.withdraw()

def quit_app():
    """Quit the application completely"""
    if tray_icon:
        tray_icon.stop()
    root.quit()
    sys.exit()

def setup_tray():
    """Setup the system tray icon"""
    global tray_icon
    
    # Create tray menu
    menu = pystray.Menu(
        pystray.MenuItem("Show CaseCon", show_window, default=True),
        pystray.MenuItem("Hide CaseCon", hide_window),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app)
    )
    
    # Create tray icon
    icon_image = create_tray_icon()
    tray_icon = pystray.Icon("CaseCon", icon_image, "CaseCon - Text Case Converter", menu)
    
    # Run tray icon in a separate thread
    tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
    tray_thread.start()

# Global tray icon variable
tray_icon = None

# -------------------- Main Window --------------------
root = tk.Tk()
root.title("CaseCon")
root.geometry("460x500")
root.resizable(False, False)

# Set window icon
try:
    icon_path = os.path.join(script_dir, "icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        print(f"Icon file not found at: {icon_path}")
except Exception as e:
    print(f"Failed to load icon: {e}")
    log_error(f"Failed to load icon: {str(e)}")

# Handle window close event
def on_closing():
    if get_setting("start_hidden_tray"):
        hide_window()
    else:
        quit_app()

root.protocol("WM_DELETE_WINDOW", on_closing)

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

tab_tray = tk.Frame(notebook, bg='#f0f0f0')
notebook.add(tab_tray, text="Minimize to tray")

# Remove the extra minimize button we added
# minimize_tray_btn = tk.Button(root, text="→ Tray", font=("Arial", 8), 
#                              width=8, height=1, command=hide_window)
# minimize_tray_btn.grid(row=0, column=3, sticky="ne", padx=5, pady=2)

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
    is_checked = start_with_windows_var.get()
    update_setting("start_with_windows", is_checked)
    
    # Add or remove from Windows startup
    if is_checked:
        add_to_startup()
    else:
        remove_from_startup()

tk.Checkbutton(settings_frame, text="Start with Windows", variable=start_with_windows_var, command=on_start_with_windows_change, bg='#f0f0f0')\
    .grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 0))
row += 1

start_hidden_tray_var = tk.IntVar(value=get_setting("start_hidden_tray"))
def on_start_hidden_tray_change():
    update_setting("start_hidden_tray", start_hidden_tray_var.get())
tk.Checkbutton(settings_frame, text="Always hide in system tray", variable=start_hidden_tray_var, command=on_start_hidden_tray_change, bg='#f0f0f0')\
    .grid(row=row, column=0, columnspan=2, sticky="w", pady=(5, 0))

# -------------------- Tray Tab --------------------
# This tab automatically minimizes to tray when selected
def on_tray_tab_selected():
    hide_window()

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

notebook.bind("<<NotebookTabChanged>>", lambda e=None: (on_tab_changed(), root.focus()))

def on_tab_changed():
    """Handle tab selection changes"""
    current_tab = notebook.index(notebook.select())
    if current_tab == 2:  # Third tab (index 2) is the tray tab
        root.after(100, on_tray_tab_selected)  # Small delay to ensure tab is visible first

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

# Setup system tray
setup_tray()

# Sync the checkbox state with actual Windows startup status on launch
actual_startup_status = is_in_startup()
if actual_startup_status != bool(get_setting("start_with_windows")):
    update_setting("start_with_windows", int(actual_startup_status))
    start_with_windows_var.set(int(actual_startup_status))

# Check if should start hidden based on the setting
if get_setting("start_hidden_tray"):
    root.withdraw()  # Start hidden in tray
else:
    root.after(50, lambda: root.focus())  # Start normally and focus

root.mainloop()