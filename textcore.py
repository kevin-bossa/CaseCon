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
            "kebabcase": "K"
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
                    "K": 37
                }[char]
                sc = fallback_sc
            default_shortcuts[mode] = f"{CTRL_SC}+{WIN_SC}+{ALT_SC}+{sc}"

        default_settings = {
            "shortcuts": default_shortcuts,
            "start_with_windows": 0,
            "start_hidden_tray": 0
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(default_settings, f, indent=4)

        return default_settings
    else:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)


def save_json(data):
    with open(CONFIG_FILE, "w") as f:
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
    return MODES[mode](text)


# -------------------- Clipboard Conversion --------------------
last_transformed = {"text": None, "mode": None}


def convert_clipboard_text(mode, retries=10, delay=0.3):
    global last_transformed

    old_clipboard = pyperclip.paste()
    new_text = None

    for attempt in range(retries):
        try:
            keyboard.press_and_release('ctrl+c')
            time.sleep(delay)
            candidate = pyperclip.paste()
            if candidate and candidate != old_clipboard:
                new_text = candidate
                break
        except Exception as e:
            print(f"Error during Ctrl+C attempt {attempt + 1}: {e}")
    else:
        raise RuntimeError("Could not read the selected text. Make sure Ctrl+C works.")

    # Only skip if both text and mode are the same as the last transformation
    if (last_transformed["text"]
            and new_text.casefold() == last_transformed["text"].casefold()
            and last_transformed["mode"] == mode):
        return

    try:
        transformed = transform_text(new_text, mode)
        last_transformed["text"] = new_text
        last_transformed["mode"] = mode
        pyperclip.copy(transformed)
        keyboard.press_and_release('ctrl+v')
        time.sleep(0.1)
        pyperclip.copy(old_clipboard)
    except Exception as e:
        print(f"Error during transformation or paste: {e}")