import tkinter as tk
from tkinter import ttk
import keyboard
import pystray
from PIL import Image, ImageDraw
import threading
import sys
import winreg
import os
import time
import traceback
import datetime
import ctypes

# Change to script directory to ensure relative imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add error logging for startup debugging
def log_error(error_msg):
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

# -------------------- Key name handling --------------------
CTRL_SC = 29
WIN_SC = 91
ALT_SC = 56

CTRL_NAME = "CTRL"
WIN_NAME = "WIN"
ALT_NAME = "ALT"

def get_key_name(scancode):
    scancode_map = {29: 'CTRL', 91: 'WIN', 56: 'ALT'}
    if scancode in scancode_map:
        return scancode_map[scancode]
    return scancode_to_key_name(scancode)

def scancode_to_key_name(sc):
    try:
        vk = ctypes.windll.user32.MapVirtualKeyW(sc, 3)
        name_buffer = ctypes.create_unicode_buffer(64)
        lparam = sc << 16
        ctypes.windll.user32.GetKeyNameTextW(lparam, name_buffer, 64)
        return name_buffer.value.upper()
    except:
        return f"KEY_{sc}"

# -------------------- Detect scancodes for letters --------------------
def get_scancode_for_char(target_char):
    user32 = ctypes.WinDLL('user32')
    layout = user32.GetKeyboardLayout(0)  # Current layout

    MapVirtualKeyEx = user32.MapVirtualKeyExW
    MapVirtualKeyEx.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
    MapVirtualKeyEx.restype = ctypes.c_uint

    for vk in range(256):
        keyboard_state = (ctypes.c_ubyte * 256)()  # No modifiers
        char_buffer = ctypes.create_unicode_buffer(2)
        res = user32.ToUnicodeEx(vk, 0, keyboard_state, char_buffer, 2, 0, layout)
        if res > 0 and char_buffer.value.upper() == target_char.upper():
            sc = MapVirtualKeyEx(vk, 0, layout)  # Get scancode
            return sc
    return None

# -------------------- Windows startup --------------------
def add_to_startup():
    try:
        app_path = os.path.abspath(__file__)
        batch_path = os.path.join(script_dir, "start_casecon.bat")
        python_path = sys.executable.replace('python.exe', 'pythonw.exe')
        batch_content = f'@echo off\ncd /d "{script_dir}"\n"{python_path}" "{app_path}"\n'
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "CaseCon", 0, winreg.REG_SZ, f'"{batch_path}"')
        winreg.CloseKey(key)
    except Exception as e:
        log_error(f"Failed to add to startup: {str(e)}\n{traceback.format_exc()}")

def remove_from_startup():
    try:
        batch_path = os.path.join(script_dir, "start_casecon.bat")
        if os.path.exists(batch_path): os.remove(batch_path)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "CaseCon")
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    except Exception as e:
        log_error(f"Failed to remove from startup: {str(e)}\n{traceback.format_exc()}")

def is_in_startup():
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

# -------------------- System Tray --------------------
def create_tray_icon():
    try:
        icon_path = os.path.join(script_dir, "icon.ico")
        if os.path.exists(icon_path):
            return Image.open(icon_path)
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16,16,48,48], fill='white')
        draw.text((20,28), "CC", fill='black')
        return image
    except:
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16,16,48,48], fill='white')
        draw.text((20,28), "CC", fill='black')
        return image

def show_window():
    root.deiconify()
    notebook.select(tab_main)  # Always open Main tab
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))

def hide_window():
    root.withdraw()

def quit_app():
    if tray_icon: tray_icon.stop()
    root.quit()
    sys.exit()

def setup_tray():
    global tray_icon
    menu = pystray.Menu(
        pystray.MenuItem("Show CaseCon", show_window, default=True),
        pystray.MenuItem("Hide CaseCon", hide_window),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app)
    )
    icon_image = create_tray_icon()
    tray_icon = pystray.Icon("CaseCon", icon_image, "CaseCon - Text Case Converter", menu)
    threading.Thread(target=tray_icon.run, daemon=True).start()

tray_icon = None

# -------------------- Main Window --------------------
root = tk.Tk()
root.title("CaseCon")
root.geometry("460x500")
root.resizable(False, False)

try:
    icon_path = os.path.join(script_dir, "icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
except Exception as e:
    log_error(f"Failed to load icon: {str(e)}")

root.protocol("WM_DELETE_WINDOW", lambda: hide_window() if get_setting("start_hidden_tray") else quit_app())

# -------------------- Notebook --------------------
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, columnspan=4, sticky="nsew")

tab_main = tk.Frame(notebook, bg='#f0f0f0')
notebook.add(tab_main, text="Main")

tab_settings = tk.Frame(notebook, bg='#f0f0f0')
notebook.add(tab_settings, text="Settings")

tab_tray = tk.Frame(notebook, bg='#f0f0f0')
notebook.add(tab_tray, text="Minimize to tray")

def on_tab_changed(event):
    selected_tab = event.widget.select()
    if selected_tab == str(tab_tray):
        hide_window()
    elif selected_tab == str(tab_settings):
        root.focus()  # Remove focus from entries whenever Settings tab is selected

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

# -------------------- Settings Tab --------------------
settings_frame = tk.Frame(tab_settings, bg='#f0f0f0')
settings_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

shortcuts = get_shortcuts()

# -------------------- AUTO-SET DEFAULTS FOR SHORTCUTS --------------------
default_letters = {
    "uppercase": "U",
    "lowercase": "L",
    "titlecase": "T",
    "sentencecase": "C",  # 'C' from "case"
    "macrocase": "M",
    "snakecase": "S",
    "pascalcase": "P",
    "kebabcase": "K"
}

for mode, char in default_letters.items():
    if shortcuts.get(mode, "").upper() == "NONE":
        sc = get_scancode_for_char(char)
        if sc is None:  # fallback to US layout
            fallback_map = {"U":22, "L":38, "T":20, "C":46, "M":50, "S":31, "P":25, "K":37}
            sc = fallback_map[char]
        default_shortcut = f"{CTRL_SC}+{WIN_SC}+{ALT_SC}+{sc}"
        update_shortcut(mode, default_shortcut)
        shortcuts[mode] = default_shortcut

entry_widgets = {}
row = 0
for mode, default in shortcuts.items():
    tk.Label(settings_frame, text=mode.capitalize() + ":", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
    e = tk.Entry(settings_frame, width=35)

    if default.upper() == "NONE":
        e.insert(0, "NONE")
    else:
        try:
            sc_list = [int(sc) for sc in default.split('+')]
            display_parts = [get_key_name(sc) for sc in sc_list]
            e.insert(0, '+'.join(display_parts))
        except:
            e.insert(0, "NONE")

    e.grid(row=row, column=1, padx=(10,0), pady=5)
    entry_widgets[mode] = e
    row += 1

start_with_windows_var = tk.IntVar(value=get_setting("start_with_windows"))
tk.Checkbutton(settings_frame, text="Start with Windows", variable=start_with_windows_var,
               command=lambda: add_to_startup() if start_with_windows_var.get() else remove_from_startup(),
               bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky="w", pady=(10,0))
row += 1

start_hidden_tray_var = tk.IntVar(value=get_setting("start_hidden_tray"))
tk.Checkbutton(settings_frame, text="Always hide in system tray", variable=start_hidden_tray_var,
               command=lambda: update_setting("start_hidden_tray", start_hidden_tray_var.get()),
               bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky="w", pady=(5,0))

root.focus()

# -------------------- Hotkeys Setup --------------------
dynamic_shortcuts = {mode: shortcuts[mode] for mode in shortcuts}
hotkey_handles = []

def register_hotkeys():
    global hotkey_handles
    for handle in hotkey_handles:
        try:
            keyboard.remove_hotkey(handle)
        except (KeyError, ValueError):
            pass
    hotkey_handles = []

    for mode, shortcut_sc in dynamic_shortcuts.items():
        if not shortcut_sc or shortcut_sc.upper() == "NONE":
            continue
        try:
            scancodes = [int(sc) for sc in shortcut_sc.split('+')]
            handle = keyboard.add_hotkey(scancodes, lambda m=mode: convert_clipboard_text(m), suppress=False)
            hotkey_handles.append(handle)
        except Exception as e:
            log_error(f"Failed to register hotkey {shortcut_sc} for {mode}: {str(e)}")

register_hotkeys()

# -------------------- Shortcut Recording --------------------
current_entry = None
previous_value = ""
recorded_key_name = None

def start_recording(entry):
    global current_entry, previous_value, recorded_key_name
    if current_entry:
        current_entry.delete(0, tk.END)
        current_entry.insert(0, previous_value)
        current_entry.config(bg='white', insertontime=600, state='normal')
        keyboard.unhook_all()
        current_entry = None
        recorded_key_name = None

    for handle in hotkey_handles:
        try:
            keyboard.remove_hotkey(handle)
        except (KeyError, ValueError):
            pass
    hotkey_handles.clear()

    previous_value = entry.get()
    current_entry = entry
    entry.delete(0, tk.END)
    entry.insert(0, "PRESS LETTER/NUMBER OR DELETE")
    entry.icursor(tk.END)
    entry.config(bg='#e8e8e8', insertontime=0, state='readonly')

    def on_key_event(event):
        if event.event_type != keyboard.KEY_DOWN:
            return
        key_name = event.name.upper()
        if key_name == 'MAYUSCULAS':
            key_name = 'SHIFT'

        if key_name == 'DELETE':
            finish_recording("NONE")
            return True

        if key_name in ('ESC', 'ENTER'):
            finish_recording(previous_value)
            return False

        if len(key_name) == 1 and key_name.isalnum():
            global recorded_key_name
            recorded_key_name = key_name
            final_sc = str(event.scan_code)
            shortcut_sc = f"{CTRL_SC}+{WIN_SC}+{ALT_SC}+{final_sc}"
            finish_recording(shortcut_sc)
            return False

    def finish_recording(shortcut_sc):
        keyboard.unhook_all()
        root.after(10, lambda: stop_recording(entry, shortcut_sc))

    keyboard.hook(on_key_event)

def stop_recording(entry, shortcut_sc):
    global current_entry, previous_value, recorded_key_name

    entry.config(state='normal')
    if shortcut_sc.upper() == "NONE":
        display_text = "NONE"
    else:
        try:
            sc_list = [int(sc) for sc in shortcut_sc.split('+')]
            display_parts = [get_key_name(sc) if sc in (CTRL_SC, WIN_SC, ALT_SC) or not recorded_key_name else recorded_key_name for sc in sc_list]
            display_text = '+'.join(display_parts)
        except Exception as e:
            display_text = "NONE"
            log_error(f"Error converting scancodes to display text: {str(e)}")

    entry.delete(0, tk.END)
    entry.insert(0, display_text)
    entry.config(bg='white', insertontime=600)
    current_entry = None
    previous_value = display_text
    recorded_key_name = None

    root.focus()

    mode = next((m for m,e in entry_widgets.items() if e==entry), None)
    if mode:
        update_shortcut(mode, shortcut_sc if shortcut_sc != "NONE" else "NONE")
        dynamic_shortcuts[mode] = shortcut_sc if shortcut_sc != "NONE" else "NONE"
        register_hotkeys()

for entry in entry_widgets.values():
    entry.bind("<Button-1>", lambda e, entry=entry: (start_recording(entry), "break"))
    entry.bind("<FocusIn>", lambda e, entry=entry: entry.icursor(tk.END))

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

# -------------------- Setup Tray --------------------
setup_tray()

# Sync startup status
actual_startup_status = is_in_startup()
if actual_startup_status != bool(get_setting("start_with_windows")):
    update_setting("start_with_windows", int(actual_startup_status))
    start_with_windows_var.set(int(actual_startup_status))

if get_setting("start_hidden_tray"):
    root.withdraw()
else:
    root.after(50, lambda: root.focus())

root.mainloop()
