import re

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

def transform_text(text, mode):
    return MODES[mode](text)

def main():
    while True:
        text = input("Enter text (or exit to quit)")
        if text.lower() == "exit":
            break
        mode = input("Enter mode:")
        transformed = transform_text(text, mode)
        print(f"Transformed text: {transformed}\n")
        
if __name__ == "__main__":
    main()



