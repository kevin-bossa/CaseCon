class TextModes:
    @staticmethod
    def snake_case(text)

    @staticmethod
    def kebab_case(text)

    @staticmethod
    def camel_case(text)

    @staticmethod
    def pascal_case(text)

    @staticmethod
    def upper_snake_case(text)
    
MODES = {
    "uppercase" : str.upper,
    "lowercase" : str.lower,
    "titlecase" : str.title,
    "sentencecase" : str.capitalize,
    "snakecase": snake_case,
    "kebabcase": kebab_case,
    "camelcase": camel_case,
    "pascalcase": pascal_case,
    "uppersnakecase": upper_snake_case,
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
main()



