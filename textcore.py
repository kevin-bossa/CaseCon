import re
import keyboard
import pyperclip
import time
import json
import os

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

# -------------------- JSON Settings Management --------------------
def load_json():
    if not os.path.exists(CONFIG_FILE):
        default_settings = {
            "shortcuts": {
                "uppercase": "ctrl+shift+u",
                "lowercase": "ctrl+shift+l",
                "titlecase": "ctrl+shift+t",
                "sentencecase": "ctrl+shift+s",
                "macrocase": "ctrl+shift+m",
                "snakecase": "ctrl+shift+z",
                "pascalcase": "ctrl+shift+p",
                "kebabcase": "ctrl+shift+k"
            },
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
    return data.get(key, 0)  # Default to 0 for boolean settings

def update_setting(key, value):
    data = load_json()
    data[key] = value
    save_json(data)

# -------------------- Transform Function --------------------
def transform_text(text, mode):
    return MODES[mode](text)

# -------------------- Clipboard Conversion --------------------
last_transformed = {"text": None, "mode": None}

def convert_clipboard_text(mode, retries=10, delay=0.3):  # Increased delay for reliability
    global last_transformed
    old_clipboard = pyperclip.paste()
    new_text = None

    print(f"Attempting to convert clipboard text to {mode}")  # Debug: Log mode
    for attempt in range(retries):
        try:
            keyboard.press_and_release('ctrl+c')
            time.sleep(delay)  # Increased delay to ensure clipboard updates
            candidate = pyperclip.paste()
            print(f"Attempt {attempt + 1}: Clipboard content = '{candidate}'")  # Debug: Log clipboard content
            if candidate and candidate != old_clipboard:
                new_text = candidate
                break
        except Exception as e:
            print(f"Error during Ctrl+C attempt {attempt + 1}: {e}")  # Debug: Log errors
    else:
        print("Failed to read selected text after retries")  # Debug: Log failure
        raise RuntimeError("Could not read the selected text. Make sure Ctrl+C works.")

    # Skip transformation if the text and mode are the same as the last transformation
    if last_transformed["text"] and new_text.casefold() == last_transformed["text"].casefold() \
       and last_transformed["mode"] == mode:
        print(f"Skipping transformation: same text and mode ({mode})")  # Debug: Log skip
        return

    try:
        transformed = transform_text(new_text, mode)
        print(f"Transformed text: '{transformed}'")  # Debug: Log transformed text
        last_transformed["text"] = new_text
        last_transformed["mode"] = mode

        pyperclip.copy(transformed)
        print("Copied transformed text to clipboard")  # Debug: Log clipboard copy
        keyboard.press_and_release('ctrl+v')
        time.sleep(0.1)  # Increased delay for paste reliability
        print("Pasted transformed text")  # Debug: Log paste action
        pyperclip.copy(old_clipboard)
        print("Restored original clipboard content")  # Debug: Log clipboard restore
    except Exception as e:
        print(f"Error during transformation or paste: {e}")  # Debug: Log errors