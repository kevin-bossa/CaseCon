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
import atexit
from tkinter import messagebox  # used for popups

# Change to script directory to ensure relative imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add error logging for startup debugging
def log_error(error_msg):
    try:
        with open("casecon_error.log", "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {error_msg}\n")
    except:
        pass

try:
    from textcore import (
        transform_text,
        convert_clipboard_text,
        get_shortcuts,
        update_shortcut,
        get_setting,
        update_setting,
        count_selected_text,
    )
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

def get_scancode_for_char(target_char):
    user32 = ctypes.WinDLL('user32')
    layout = user32.GetKeyboardLayout(0)
    MapVirtualKeyEx = user32.MapVirtualKeyExW
    MapVirtualKeyEx.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
    MapVirtualKeyEx.restype = ctypes.c_uint
    for vk in range(256):
        keyboard_state = (ctypes.c_ubyte * 256)()
        char_buffer = ctypes.create_unicode_buffer(2)
        res = user32.ToUnicodeEx(vk, 0, keyboard_state, char_buffer, 2, 0, layout)
        if res > 0 and char_buffer.value.upper() == target_char.upper():
            sc = MapVirtualKeyEx(vk, 0, layout)
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
    notebook.select(tab_main)
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))

def hide_window():
    root.withdraw()

def quit_app():
    global app_running
    app_running = False
    complete_shutdown()
    if tray_icon:
        try:
            tray_icon.stop()
        except:
            pass
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
        root.focus()

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

# -------------------- Settings Tab --------------------
settings_frame = tk.Frame(tab_settings, bg='#f0f0f0')
settings_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

shortcuts = get_shortcuts()

# -------------------- DEFAULT SHORTCUTS (only first run) --------------------
default_letters = {
    "uppercase": "U",
    "lowercase": "L",
    "titlecase": "T",
    "sentencecase": "Z",  # Changed to Z
    "macrocase": "M",
    "snakecase": "S",
    "pascalcase": "P",
    "kebabcase": "K",
    "count": "C",  # Changed to C
    "launch": "V"  # Changed to V
}

# Apply defaults only if shortcut is empty string
for mode, char in default_letters.items():
    current_value = shortcuts.get(mode, "")
    if current_value == "":
        sc = get_scancode_for_char(char) or {"U":22,"L":38,"T":20,"Z":44,"M":50,"S":31,"P":25,"K":37,"C":46,"V":47}[char]
        default_shortcut = f"{CTRL_SC}+{WIN_SC}+{ALT_SC}+{sc}"
        update_shortcut(mode, default_shortcut)
        shortcuts[mode] = default_shortcut

# Add SHORTCUTS title
tk.Label(settings_frame, text="SHORTCUTS", bg='#f0f0f0', font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0,5))

entry_widgets = {}
row = 1
for mode, default in shortcuts.items():
    tk.Label(settings_frame, text=mode.capitalize() + ":", bg='#f0f0f0', font=("Arial", 9)).grid(row=row, column=0, sticky="w", pady=3)
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

    e.grid(row=row, column=1, padx=(10,0), pady=3)
    
    # Add small reset button ↺
    def make_reset_callback(entry=e, m=mode, default_char=default_letters.get(mode, None)):
        def reset_shortcut():
            if default_char:
                sc = get_scancode_for_char(default_char) or {"U":22,"L":38,"T":20,"Z":44,"M":50,"S":31,"P":25,"K":37,"C":46,"V":47}[default_char]
                default_shortcut = f"{CTRL_SC}+{WIN_SC}+{ALT_SC}+{sc}"
                update_shortcut(m, default_shortcut)
                entry.delete(0, tk.END)
                sc_list = [int(sc) for sc in default_shortcut.split('+')]
                display_parts = [get_key_name(sc) for sc in sc_list]
                entry.insert(0, '+'.join(display_parts))
                update_dynamic_shortcut(m, default_shortcut)
        return reset_shortcut
    reset_btn = tk.Button(settings_frame, text="↺", width=2, command=make_reset_callback())
    reset_btn.grid(row=row, column=2, padx=(5,0))

    # Add new Cancel button ✖
    def make_cancel_callback(entry=e, m=mode):
        def cancel_shortcut():
            global current_entry, recording_active
            if current_entry == entry and recording_active:
                stop_recording_immediately()
                stop_recording(entry, "NONE")
            else:
                entry.delete(0, tk.END)
                entry.insert(0, "NONE")
                update_shortcut(m, "NONE")
                update_dynamic_shortcut(m, "NONE")
        return cancel_shortcut
    cancel_btn = tk.Button(settings_frame, text="✖", width=2, fg="red", command=make_cancel_callback())
    cancel_btn.grid(row=row, column=3, padx=(5,0))
    
    entry_widgets[mode] = e
    row += 1

# Add "Restore All Shortcuts" button
def restore_all_shortcuts():
    """Restore all shortcuts to their default values"""
    for mode, default_char in default_letters.items():
        if default_char:
            sc = get_scancode_for_char(default_char) or {"U":22,"L":38,"T":20,"Z":44,"M":50,"S":31,"P":25,"K":37,"C":46,"V":47}[default_char]
            default_shortcut = f"{CTRL_SC}+{WIN_SC}+{ALT_SC}+{sc}"
            
            # Update the shortcut in storage and dynamic shortcuts
            update_shortcut(mode, default_shortcut)
            update_dynamic_shortcut(mode, default_shortcut)
            
            # Update the display in the entry field
            if mode in entry_widgets:
                entry = entry_widgets[mode]
                entry.delete(0, tk.END)
                sc_list = [int(sc) for sc in default_shortcut.split('+')]
                display_parts = [get_key_name(sc) for sc in sc_list]
                entry.insert(0, '+'.join(display_parts))

restore_all_btn = tk.Button(settings_frame, text="Restore All Shortcuts", 
                           command=restore_all_shortcuts)
restore_all_btn.grid(row=row, column=1, pady=(5,10))
row += 1

# Add STARTUP SETTINGS title
tk.Label(settings_frame, text="STARTUP SETTINGS", bg='#f0f0f0', font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=4, sticky="w", pady=(0,3))
row += 1

start_with_windows_var = tk.IntVar(value=get_setting("start_with_windows"))
tk.Checkbutton(settings_frame, text="Start with Windows", variable=start_with_windows_var,
               command=lambda: add_to_startup() if start_with_windows_var.get() else remove_from_startup(),
               bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky="w", pady=(5,0))
row += 1

start_hidden_tray_var = tk.IntVar(value=get_setting("start_hidden_tray"))
tk.Checkbutton(settings_frame, text="Always hide in system tray", variable=start_hidden_tray_var,
               command=lambda: update_setting("start_hidden_tray", start_hidden_tray_var.get()),
               bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky="w", pady=(5,0))

root.focus()

# -------------------- SINGLE PERSISTENT HOOK SYSTEM --------------------
app_running = True
dynamic_shortcuts = {mode: shortcuts[mode] for mode in shortcuts}
shortcut_lock = threading.Lock()
recording_active = False
main_hook_active = False
count_popup_active = False  # NEW: Flag to track if count popup is active

# Track currently pressed keys manually
pressed_scancodes = set()
pressed_lock = threading.Lock()

# small cooldown to prevent repeated triggers while holding the keys
last_trigger_time = 0.0
TRIGGER_COOLDOWN = 0.35  # seconds

def update_dynamic_shortcut(mode, shortcut_sc):
    """Thread-safe shortcut update"""
    with shortcut_lock:
        dynamic_shortcuts[mode] = shortcut_sc

def parse_shortcut_combination(shortcut_sc):
    """Convert shortcut string to scancode list"""
    if not shortcut_sc or shortcut_sc.upper() == "NONE":
        return None
    try:
        return [int(sc) for sc in shortcut_sc.split('+')]
    except:
        return None

def clear_pressed_scancodes():
    """Clear pressed scancodes safely (used to recover from missed KEY_UP events)."""
    with pressed_lock:
        pressed_scancodes.clear()

def check_key_combination_match(target_combination):
    """Check if the current pressed keys contain the target combination (subset check)."""
    if not target_combination:
        return False
    with pressed_lock:
        target_set = set(target_combination)
        # use subset instead of strict equality to be tolerant of timing / extra keys
        return target_set.issubset(pressed_scancodes)

def global_key_handler(event):
    """Single global key handler that tracks key states and checks shortcuts"""
    global recording_active, pressed_scancodes, last_trigger_time
    
    if not app_running:
        return
    
    # Update our pressed keys tracking (always update — do not ignore user presses)
    with pressed_lock:
        if event.event_type == keyboard.KEY_DOWN:
            pressed_scancodes.add(event.scan_code)
        elif event.event_type == keyboard.KEY_UP:
            pressed_scancodes.discard(event.scan_code)
    
    # Handle recording mode separately
    if recording_active:
        handle_recording_key(event)
        return
    
    # Only process key down events for hotkeys
    if event.event_type != keyboard.KEY_DOWN:
        return
    
    # Check each registered shortcut
    with shortcut_lock:
        for mode, shortcut_sc in dynamic_shortcuts.items():
            target_combination = parse_shortcut_combination(shortcut_sc)
            if target_combination and check_key_combination_match(target_combination):
                now = time.time()
                if now - last_trigger_time < TRIGGER_COOLDOWN:
                    # still in cooldown, ignore repeated triggers from holding the keys
                    return
                last_trigger_time = now
                # Start conversion in a separate thread (non-blocking)
                threading.Thread(
                    target=execute_transformation, 
                    args=(mode,), 
                    daemon=True
                ).start()
                # Schedule a quick cleanup in case some KEY_UP events were missed
                threading.Timer(0.25, clear_pressed_scancodes).start()
                break  # Only execute one transformation per key press

def execute_transformation(mode):
    """Execute text transformation safely. If mode == 'count' -> show popup with counts. If mode == 'launch' -> show window."""
    global count_popup_active
    try:
        if mode == "count":
            if count_popup_active:
                return  # Silently ignore if a popup is already open
            try:
                result = count_selected_text()
                def show_count_popup():
                    global count_popup_active
                    try:
                        count_popup_active = True
                        messagebox.showinfo(
                            "Text Count",
                            f"Words: {result['words']} - Letters: {result['letters']} - All characters: {result['all_chars']}",
                            parent=root
                        )
                        count_popup_active = False
                    except Exception as e:
                        count_popup_active = False
                        log_error(f"Failed to show count popup: {str(e)}")
                root.after(0, show_count_popup)
            except Exception as e:
                count_popup_active = False
                log_error(f"Error counting selection: {str(e)}\n{traceback.format_exc()}")
        elif mode == "launch":
            if root.state() == 'withdrawn':  # Only show window if it's currently hidden
                root.after(0, show_window)  # Schedule show_window on main thread
        else:
            convert_clipboard_text(mode)
    except Exception as e:
        log_error(f"Error executing transformation for {mode}: {str(e)}")
    finally:
        clear_pressed_scancodes()

def initialize_global_hook():
    """Initialize the single global keyboard hook"""
    global main_hook_active
    if not main_hook_active and app_running:
        try:
            keyboard.hook(global_key_handler)
            main_hook_active = True
            log_error("Global keyboard hook initialized successfully")
        except Exception as e:
            log_error(f"Failed to initialize global hook: {str(e)}")

def cleanup_global_hook():
    """Clean up the global keyboard hook"""
    global main_hook_active, pressed_scancodes
    if main_hook_active:
        try:
            keyboard.unhook_all()
            main_hook_active = False
            with pressed_lock:
                pressed_scancodes.clear()
            log_error("Global keyboard hook cleaned up")
        except Exception as e:
            log_error(f"Error cleaning up global hook: {str(e)}")

def complete_shutdown():
    """Complete cleanup on shutdown"""
    global app_running
    app_running = False
    cleanup_global_hook()

# Register cleanup on exit
atexit.register(complete_shutdown)

# Initialize the global hook
initialize_global_hook()

# -------------------- RECORDING SYSTEM --------------------
current_entry = None
previous_value = ""
previous_shortcut_sc = ""  # NEW: Store the original shortcut scancode format
recorded_key_name = None

def handle_recording_key(event):
    """Handle key events during recording"""
    global recording_active, recorded_key_name, current_entry, previous_shortcut_sc
    
    if not recording_active or not current_entry or event.event_type != keyboard.KEY_DOWN:
        return
    
    key_name = event.name.upper()
    if key_name == 'MAYUSCULAS':
        key_name = 'SHIFT'
    
    if key_name in ('ESC', 'ENTER'):
        # FIXED: Use previous_shortcut_sc instead of previous_value to preserve original shortcut
        root.after(10, lambda: stop_recording(current_entry, previous_shortcut_sc))
        return
    
    # Accept letters, numbers, and function keys (F1-F24)
    if (len(key_name) == 1 and key_name.isalnum()) or (key_name.startswith('F') and key_name[1:].isdigit()):
        recorded_key_name = key_name
        final_sc = str(event.scan_code)
        shortcut_sc = f"{CTRL_SC}+{WIN_SC}+{ALT_SC}+{final_sc}"
        root.after(10, lambda: stop_recording(current_entry, shortcut_sc))

def stop_recording_immediately():
    """Immediately stop recording"""
    global recording_active, current_entry
    recording_active = False
    current_entry = None

def start_recording(entry):
    global current_entry, previous_value, previous_shortcut_sc, recorded_key_name, recording_active
    
    # Stop any existing recording
    stop_recording_immediately()
    
    # FIXED: Store both display value and original shortcut scancode format
    previous_value = entry.get()
    
    # Find the mode for this entry and get the original shortcut scancode format
    mode = next((m for m, e in entry_widgets.items() if e == entry), None)
    if mode:
        previous_shortcut_sc = dynamic_shortcuts.get(mode, "NONE")
    else:
        previous_shortcut_sc = "NONE"
    
    # Set up new recording
    current_entry = entry
    recording_active = True
    recorded_key_name = None
    
    entry.delete(0, tk.END)
    entry.insert(0, "PRESS LETTER/NUMBER/FUNCTION KEY")
    entry.icursor(tk.END)
    entry.config(bg='#e8e8e8', insertontime=0, state='readonly')

def stop_recording(entry, shortcut_sc):
    global current_entry, previous_value, previous_shortcut_sc, recorded_key_name, recording_active

    recording_active = False
    current_entry = None
    
    entry.config(state='normal')
    
    # Find the mode for this entry
    mode = next((m for m, e in entry_widgets.items() if e == entry), None)
    
    # Check for duplicate shortcuts (only if it's not NONE and not the same as previous)
    if shortcut_sc.upper() != "NONE" and shortcut_sc != previous_shortcut_sc:
        # Check if this shortcut is already used by another mode
        for other_mode, other_shortcut in dynamic_shortcuts.items():
            if other_mode != mode and other_shortcut == shortcut_sc:
                # Found duplicate! Show popup and revert
                from tkinter import messagebox
                try:
                    sc_list = [int(sc) for sc in shortcut_sc.split('+')]
                    display_parts = [get_key_name(sc) if sc in (CTRL_SC, WIN_SC, ALT_SC) or not recorded_key_name else recorded_key_name for sc in sc_list]
                    shortcut_display = '+'.join(display_parts)
                except:
                    shortcut_display = "this shortcut"
                
                messagebox.showwarning(
                    "Duplicate Shortcut", 
                    f"The shortcut '{shortcut_display}' is already assigned to {other_mode.capitalize()}.\n\nPlease choose a different key."
                )
                
                # Revert to previous shortcut and display it
                if previous_shortcut_sc.upper() == "NONE":
                    display_text = "NONE"
                else:
                    try:
                        sc_list = [int(sc) for sc in previous_shortcut_sc.split('+')]
                        display_parts = [get_key_name(sc) for sc in sc_list]
                        display_text = '+'.join(display_parts)
                    except:
                        display_text = "NONE"
                
                entry.delete(0, tk.END)
                entry.insert(0, display_text)
                entry.config(bg='white', insertontime=600)
                
                # Reset recording state
                previous_value = display_text
                recorded_key_name = None
                root.focus()
                
                # IMPORTANT: Return here to prevent saving the duplicate shortcut
                return
    
    # If we get here, it's not a duplicate, so proceed with saving
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
    
    # Reset recording state
    previous_value = display_text
    previous_shortcut_sc = shortcut_sc  # Update the stored shortcut scancode
    recorded_key_name = None

    root.focus()

    # Update the shortcut
    if mode:
        update_shortcut(mode, shortcut_sc if shortcut_sc != "NONE" else "NONE")
        update_dynamic_shortcut(mode, shortcut_sc if shortcut_sc != "NONE" else "NONE")

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

actual_startup_status = is_in_startup()
if actual_startup_status != bool(get_setting("start_with_windows")):
    update_setting("start_with_windows", int(actual_startup_status))
    start_with_windows_var.set(int(actual_startup_status))

if get_setting("start_hidden_tray"):
    hide_window()

# -------------------- Run --------------------
try:
    root.mainloop()
finally:
    complete_shutdown()