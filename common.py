from dataclasses import dataclass
from enum import Enum, auto



class TokenType(Enum):
    """Enumeration of token types"""

    COMMAND = auto()
    REGISTER = auto()
    LITERAL = auto()
    COMMENT = auto()
    ENDLINE = auto()
    COMPARE = auto()

    def __str__(self) -> str:
        return self.name


class TokenValue(Enum):
    """Enumeration of token values"""

    # Commands
    COMMAND_MOV = auto()
    COMMAND_CPY = auto()
    COMMAND_SET = auto()
    COMMAND_ADD = auto()
    COMMAND_SUB = auto()
    COMMAND_MUL = auto()
    COMMAND_DIV = auto()
    COMMAND_MOD = auto()
    COMMAND_POW = auto()
    COMMAND_STDOUT = auto()
    COMMAND_ENDL = auto()
    COMMAND_SETJMPP = auto()
    COMMAND_JMP = auto()
    COMMAND_JMPIF = auto()
    COMMAND_STRLEN = auto()
    COMMAND_STRAPP = auto()
    COMMAND_CHARAT = auto()
    COMMAND_SPACE = auto()

    # Comparisons
    COMPARE_EQ = auto()
    COMPARE_NEQ = auto()
    COMPARE_GT = auto()
    COMPARE_LT = auto()
    COMPARE_GTE = auto()
    COMPARE_LTE = auto()

    # Literals
    LITERAL_NUMBER = auto()
    LITERAL_STRING = auto()



@dataclass
class Token:
    """Represents a token"""

    tokenType: TokenType
    tokenValue: TokenValue | None
    value: str | float

    def __str__(self) -> str:
        return f"{self.tokenType}"

    def __repr__(self) -> str:
        if isinstance(self.value, str):
            value = self.value.replace("\n", "\\n")
        else:
            value = self.value

        return f'{self.tokenType}<{self.tokenValue}>: "{value}"'
    
COMMAND_MAP = {
    "mov": TokenValue.COMMAND_MOV,
    "cpy": TokenValue.COMMAND_CPY,
    "set": TokenValue.COMMAND_SET,
    "add": TokenValue.COMMAND_ADD,
    "sub": TokenValue.COMMAND_SUB,
    "mul": TokenValue.COMMAND_MUL,
    "div": TokenValue.COMMAND_DIV,
    "mod": TokenValue.COMMAND_MOD,
    "pow": TokenValue.COMMAND_POW,
    "stdout": TokenValue.COMMAND_STDOUT,
    "endl": TokenValue.COMMAND_ENDL,
    "setjmpp": TokenValue.COMMAND_SETJMPP,
    "jmp": TokenValue.COMMAND_JMP,
    "jmpif": TokenValue.COMMAND_JMPIF,
    "strlen": TokenValue.COMMAND_STRLEN,
    "strapp": TokenValue.COMMAND_STRAPP,
    "charat": TokenValue.COMMAND_CHARAT,
    ",": TokenValue.COMMAND_SPACE,
}

COMPARE_MAP = {
    "=": TokenValue.COMPARE_EQ,
    "!=": TokenValue.COMPARE_NEQ,
    ">": TokenValue.COMPARE_GT,
    "<": TokenValue.COMPARE_LT,
    ">=": TokenValue.COMPARE_GTE,
    "<=": TokenValue.COMPARE_LTE,
}

