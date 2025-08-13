import re

class TextModes:
    @staticmethod
    def snake_case(text):
        return (re.sub(r'\s+', '_', text)).lower()

    @staticmethod
    def kebab_case(text):
        return (re.sub(r'\s+', '-', text)).lower()
    @staticmethod
    def camel_case(text):
        words = text.split()
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    @staticmethod
    def pascal_case(text):
        return ''.join(word.capitalize() for word in text.split())

    @staticmethod
    def upper_snake_case(text):
        return (re.sub(r'\s+', '_', text)).upper()
    
MODES = {
    "uppercase" : str.upper,
    "lowercase" : str.lower,
    "titlecase" : str.title,
    "sentencecase" : str.capitalize,
    "snakecase": TextModes.snake_case,
    "kebabcase": TextModes.kebab_case,
    "camelcase": TextModes.camel_case,
    "pascalcase": TextModes.pascal_case,
    "uppersnakecase": TextModes.upper_snake_case,
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



