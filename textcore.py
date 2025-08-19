import re
import keyboard
import pyperclip
import time
import json
import os
import ctypes

CONFIG_FILE = "settings.json"


# -------------------- Text Modes --------------------
class TextModes:
    @staticmethod
    def macro_case(text):
        return re.sub(r'\s+', '_', text).upper()

    @staticmethod
    def snake_case(text):
        return re.sub(r'\s+', '_', text).lower()

    @staticmethod
    def pascal_case(text):
        return ''.join(word.capitalize() for word in text.split())

    @staticmethod
    def kebab_case(text):
        return re.sub(r'\s+', '-', text).lower()


# -------------------- Modes Dictionary --------------------
MODES = {
    "uppercase": str.upper,
    "lowercase": str.lower,
    "titlecase": str.title,
    "sentencecase": str.capitalize,
    "macrocase": TextModes.macro_case,
    "snakecase": TextModes.snake_case,
    "pascalcase": TextModes.pascal_case,
    "kebabcase": TextModes.kebab_case,
    # NOTE: "count" and "launch" are intentionally NOT in MODES because they do not transform text.
}


# -------------------- Helpers for scancodes --------------------
CTRL_SC = 29
WIN_SC = 91
ALT_SC = 56


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


# -------------------- JSON Settings Management --------------------
def load_json():
    if not os.path.exists(CONFIG_FILE):  # First run defaults
        default_letters = {
            "uppercase": "U",
            "lowercase": "L",
            "titlecase": "T",
            "sentencecase": "C",
            "macrocase": "M",
            "snakecase": "S",
            "pascalcase": "P",
            "kebabcase": "K",
            "count": "0",
            "launch": "J"  # Added
        }

        default_shortcuts = {}
        for mode, char in default_letters.items():
            sc = get_scancode_for_char(char)
            if sc is None:  # fallback scancodes if mapping fails
                fallback_sc = {
                    "U": 22,
                    "L": 38,
                    "T": 20,
                    "C": 46,
                    "M": 50,
                    "S": 31,
                    "P": 25,
                    "K": 37,
                    "0": 48,
                    "J": 24  # Added
                }[char]
                sc = fallback_sc
            default_shortcuts[mode] = f"{CTRL_SC}+{WIN_SC}+{ALT_SC}+{sc}"

        default_settings = {
            "shortcuts": default_shortcuts,
            "start_with_windows": 0,
            "start_hidden_tray": 0
        }

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=4)

        return default_settings
    else:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def save_json(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_shortcuts():
    data = load_json()
    return data.get("shortcuts", {})


def update_shortcut(mode, value):
    data = load_json()
    if "shortcuts" not in data:
        data["shortcuts"] = {}
    data["shortcuts"][mode] = value
    save_json(data)


def get_setting(key):
    data = load_json()
    return data.get(key, 0)


def update_setting(key, value):
    data = load_json()
    data[key] = value
    save_json(data)


# -------------------- Transform Function --------------------
def transform_text(text, mode):
    # More robust: if mode unknown (for example "count" or "launch"), return original text unchanged.
    func = MODES.get(mode)
    if func:
        return func(text)
    return text


# -------------------- Clipboard Conversion --------------------
last_transformed = {"text": None, "mode": None}


def convert_clipboard_text(mode, retries=10):
    global last_transformed

    old_clipboard = pyperclip.paste()
    new_text = None

    # Try to grab fresh clipboard content
    for attempt in range(retries):
        keyboard.press_and_release('ctrl+c')
        for _ in range(10):  # up to 0.5s total
            time.sleep(0.05)
            candidate = pyperclip.paste()
            if candidate and candidate != old_clipboard:
                new_text = candidate
                break
        if new_text:
            break
    else:
        raise RuntimeError("Could not read the selected text. Make sure Ctrl+C works.")

    # Always re-transform (remove aggressive skipping)
    transformed = transform_text(new_text, mode)
    last_transformed["text"] = new_text
    last_transformed["mode"] = mode

    pyperclip.copy(transformed)
    keyboard.press_and_release('ctrl+v')
    time.sleep(0.2)  # allow paste to finish
    pyperclip.copy(old_clipboard)


# -------------------- NEW: Count (read selection and compute counts) --------------------
def count_selected_text(retries=10):
    """
    Copies the currently selected text (presses Ctrl+C similarly to convert_clipboard_text),
    returns a dict with 'text', 'words', 'letters', 'all_chars'.
    Restores the previous clipboard contents after reading.
    This function does not paste anything back.
    """
    old_clipboard = pyperclip.paste()
    new_text = None

    for attempt in range(retries):
        keyboard.press_and_release('ctrl+c')
        for _ in range(10):  # up to 0.5s
            time.sleep(0.05)
            candidate = pyperclip.paste()
            # accept a candidate even if equal to old_clipboard (selected text may be same)
            if candidate is not None and candidate != "":
                # If it changed AND is not empty, take it
                if candidate != old_clipboard:
                    new_text = candidate
                    break
                # If it didn't change but not empty, maybe the selection equals clipboard already
                elif attempt == retries - 1:
                    new_text = candidate
                    break
        if new_text:
            break

    # Fallback: if nothing new, use old_clipboard (last-known text)
    if new_text is None:
        new_text = old_clipboard or ""

    words = len(new_text.split())
    letters = sum(1 for c in new_text if c.isalpha())
    all_chars = len(new_text)

    # restore previous clipboard so we don't disturb user's clipboard
    try:
        pyperclip.copy(old_clipboard)
    except Exception:
        pass

    return {"text": new_text, "words": words, "letters": letters, "all_chars": all_chars}