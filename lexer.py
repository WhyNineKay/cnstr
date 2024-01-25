from common import TokenType, TokenValue, Token, COMMAND_MAP, COMPARE_MAP
from config import COMMENT_PREFIX
import utils


class Lexer:
    """Tokenizes the input source code"""

    def __init__(self, source: str) -> None:
        self._source = source
        self._tokens: list[Token] = []
        self._lineNum = 0
        self._errors: list[str] = []

    def tokenize(self) -> list[Token]:
        """
        Tokenizes the source code and returns a list of tokens
        """
        lines = self._source.splitlines()

        for i, line in enumerate(lines):
            self._lineNum = i

            tokens = self.tokenizeLine(line)

            self._tokens.extend(tokens)

        if len(self._errors) > 0:
            print(f"Encountered {len(self._errors)} errors while tokenizing:")
            print("\n".join(self._errors))
            exit(1)

        return self._tokens

    def tokenizeLine(self, line: str) -> list[Token]:
        """
        Tokenizes a given line of text into a list of tokens.
        """
        tokens: list[Token] = []

        # Check if the line is a comment.
        if line.startswith(COMMENT_PREFIX):
            tokens.append(Token(TokenType.COMMENT, None, line.rstrip("\n")))
            tokens.append(Token(TokenType.ENDLINE, None, "\n"))
            return tokens

        splitted = line.removesuffix("\n")
        splitted = utils.smart_split(splitted, includeQuotes=True)

        for rawToken in splitted:
            if rawToken == "":
                continue

            # Try for register -> literal -> label -> command.
            if rawToken.startswith("r"):
                self._parseRegister(rawToken, tokens)
            elif utils.is_number(rawToken):
                self._parseLiteralNumber(rawToken, tokens)
            elif (rawToken.startswith("'") and rawToken.endswith("'")) or (
                rawToken.startswith('"') and rawToken.endswith('"')
            ):
                self._parseLiteralString(rawToken, tokens)
            elif rawToken in COMMAND_MAP.keys():
                self._parseCommand(rawToken, tokens)
            elif rawToken in COMPARE_MAP.keys():
                self._parseComparison(rawToken, tokens)
            else:
                self.error(f"Invalid token: {rawToken}")

        tokens.append(Token(TokenType.ENDLINE, None, "\n"))

        return tokens

    def error(self, message: str) -> None:
        self._errors.append(f"Error on line {self._lineNum}\n - {message}")

    def _parseRegister(self, rawToken: str, tokens: list[Token]) -> None:
        if len(rawToken) not in (2, 3):
            self.error(
                f"Invalid register: '{rawToken}'. Register must be in the format 'rX', 'rXX'"
            )
            return

        # Register can be alnum, but not uppercase
        registerId = rawToken[1:]
        if not registerId.isalnum() or registerId.lower() != registerId:
            self.error(
                f"Invalid register: '{rawToken}'. Register must be alphanumeric, lowercase."
            )
            return

        tokens.append(Token(TokenType.REGISTER, None, rawToken))

    def _parseLiteralNumber(self, rawToken: str, tokens: list[Token]) -> None:
        tokens.append(
            Token(TokenType.LITERAL, TokenValue.LITERAL_NUMBER, float(rawToken))
        )

    def _parseLiteralString(self, rawToken: str, tokens: list[Token]) -> None:
        tokens.append(
            Token(TokenType.LITERAL, TokenValue.LITERAL_STRING, rawToken[1:-1])
        )

    def _parseCommand(self, rawToken: str, tokens: list[Token]) -> None:
        command = COMMAND_MAP[rawToken]

        tokens.append(Token(TokenType.COMMAND, command, rawToken))

    def _parseComparison(self, rawToken: str, tokens: list[Token]) -> None:
        comparison = COMPARE_MAP[rawToken]

        tokens.append(Token(TokenType.COMPARE, comparison, rawToken))
from common import TokenType, TokenValue, Token, COMMAND_MAP, COMPARE_MAP
