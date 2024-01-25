"""
CNSTR (construct)
Assembly but worse.

"""

from lexer import Lexer
from interpreter import Interpreter


def main() -> None:
    with open("source.txt", "r") as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    print("*" * 20)

    interpreter = Interpreter(tokens)
    interpreter.interpret()

    print("*" * 20)
    print(f"registers: {interpreter._registers}")
    print(f"jmp points: {interpreter._jumpPoints}")


if __name__ == "__main__":
    main()
