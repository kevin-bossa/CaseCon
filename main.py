import re
import keyboard
import pyperclip
import time

class TextModes:

    @staticmethod
    def macro_case(text):
        return (re.sub(r'\s+', '_', text)).upper()

    @staticmethod
    def snake_case(text):
        return (re.sub(r'\s+', '_', text)).lower()
        
    @staticmethod
    def pascal_case(text):
        return ''.join(word.capitalize() for word in text.split())
    
    @staticmethod
    def kebab_case(text):
        return (re.sub(r'\s+', '-', text)).lower()
    
MODES = {
    "uppercase" : str.upper,
    "lowercase" : str.lower,
    "titlecase" : str.title,
    "sentencecase" : str.capitalize,
    "macrocase": TextModes.macro_case,
    "snakecase": TextModes.snake_case,
    "pascalcase": TextModes.pascal_case,
    "kebabcase": TextModes.kebab_case,
}

SHORTCUTS = {
    "uppercase" : "ctrl+shift+u",
    "lowercase" : "ctrl+shift+l",
    "titlecase": "ctrl+shift+t",
    "sentencecase": "ctrl+shift+s",
    "macrocase": "ctrl+shift+m",
    "snakecase": "ctrl+shift+z",
    "pascalcase": "ctrl+shift+p",
    "kebabcase": "ctrl+shift+k",
}

def transform_text(text, mode):
    return MODES[mode](text)

# Track last transformed text (case-insensitive) and mode
last_transformed = {"text": None, "mode": None}

def convert_clipboard_text(mode, retries=10, delay=0.2):
    """
    Copies the currently selected text, transforms it according to mode,
    pastes it back, and restores the previous clipboard safely.
    """
    global last_transformed

    old_clipboard = pyperclip.paste()
    new_text = None

    # Try to grab the selected text multiple times
    for _ in range(retries):
        keyboard.press_and_release('ctrl+c')
        time.sleep(delay)
        candidate = pyperclip.paste()
        if candidate and candidate != old_clipboard:
            new_text = candidate
            break
    else:
        # If we can't read the selection, raise an error
        raise RuntimeError("Could not read the selected text. Make sure Ctrl+C works in this program.")

    # Skip if we already transformed this exact text with this mode (case-insensitive)
    if last_transformed["text"] and new_text.casefold() == last_transformed["text"].casefold() \
       and last_transformed["mode"] == mode:
        return

    # Transform and paste
    transformed = transform_text(new_text, mode)
    last_transformed["text"] = new_text
    last_transformed["mode"] = mode

    pyperclip.copy(transformed)
    keyboard.press_and_release('ctrl+v')
    time.sleep(0.05)  # Ensure the system has time to paste
    pyperclip.copy(old_clipboard)  # Restore original clipboard safely

# Register hotkeys
for mode, shortcut in SHORTCUTS.items():
    if shortcut:
        keyboard.add_hotkey(shortcut, lambda m=mode: convert_clipboard_text(m))

def main():
    while True:
        text = input("Enter text (or exit to quit): ")
        if text.lower() == "exit":
            break
        mode = input("Enter mode: ")
        transformed = transform_text(text, mode)
        print(f"Transformed text: {transformed}\n")
        
if __name__ == "__main__":
    main()