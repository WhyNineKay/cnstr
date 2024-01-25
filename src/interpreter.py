from common import TokenType, TokenValue, Token, COMMAND_MAP, COMPARE_MAP


class Interpreter:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._lineNum = 0
        self._currentLine: list[Token] = []

        self._registers: dict[str, float | str] = {}
        self._jumpPoints: dict[str:int] = {"start": 0}

    def interpret(self) -> None:
        lines: list[list[Token]] = []
        currentLine: list[Token] = []

        for token in self._tokens:
            if token.tokenType == TokenType.ENDLINE:
                lines.append(currentLine)
                currentLine = []
            else:
                currentLine.append(token)

        self._presetJumpPoints(lines)

        while self._lineNum < len(lines):
            self._currentLine = lines[self._lineNum]

            self.interpretLine(self._currentLine)

            self._lineNum += 1

    def _formatTokenList(self, tokens: list[Token]) -> str:
        string = ""
        for token in tokens:
            string += token.tokenType.name
            if token.tokenValue is not None:
                string += f"<{token.tokenValue.name.removeprefix(token.tokenType.name + '_')}>"
            string += " "
        return string.rstrip()

    def _recreateLine(self, tokens: list[Token]) -> str:
        string = ""
        for token in tokens:
            if token.tokenType == TokenType.ENDLINE:
                string += "\n"
                continue

            if token.tokenType == TokenType.LITERAL:
                if token.tokenValue == TokenValue.LITERAL_STRING:
                    string += f"'{token.value}'"
                else:
                    string += str(token.value)
            else:
                string += token.value

            string += " "

        return string.rstrip()

    def _presetJumpPoints(self, lines: list[list[Token]]) -> None:
        for i, line in enumerate(lines):
            if len(line) == 0:
                continue

            command = line[0]

            if (
                command.tokenType == TokenType.COMMAND
                and command.tokenValue == TokenValue.COMMAND_SETJMPP
            ):
                self.interpretSetJumpPoint(line)

            self._lineNum = i

        self._lineNum = 0

    def interpretLine(self, line: list[Token]) -> None:
        if len(line) == 0:
            return

        command = line[0]
        if command.tokenType == TokenType.COMMENT:
            return

        elif command.tokenType != TokenType.COMMAND:
            self.raiseError(
                f"Unsupported code statement '{self._formatTokenList(line)}'."
            )

        if command.tokenValue == TokenValue.COMMAND_MOV:
            self.interpretMov(line)
        elif command.tokenValue == TokenValue.COMMAND_SET:
            self.interpretSet(line)
        elif command.tokenValue == TokenValue.COMMAND_CPY:
            self.interpretCpy(line)
        elif command.tokenValue in (
            TokenValue.COMMAND_ADD,
            TokenValue.COMMAND_SUB,
            TokenValue.COMMAND_MUL,
            TokenValue.COMMAND_DIV,
            TokenValue.COMMAND_MOD,
            TokenValue.COMMAND_POW,
        ):
            self.interpretMath(line, command.tokenValue)
        elif command.tokenValue == TokenValue.COMMAND_STDOUT:
            self.interpretStdout(line)
        elif command.tokenValue == TokenValue.COMMAND_SETJMPP:
            self.interpretSetJumpPoint(line)
        elif command.tokenValue == TokenValue.COMMAND_JMP:
            self.interpretJmp(line)
        elif command.tokenValue == TokenValue.COMMAND_JMPIF:
            self.interpretJmpIf(line)
        elif command.tokenValue == TokenValue.COMMAND_STRLEN:
            self.interpretStrlen(line)
        elif command.tokenValue == TokenValue.COMMAND_STRAPP:
            self.interpretStrapp(line)
        elif command.tokenValue == TokenValue.COMMAND_CHARAT:
            self.interpretCharAt(line)
        elif command.tokenValue == TokenValue.COMMAND_SPACE:
            pass
        else:
            self.raiseError(f"Unsupported command '{command.value}'.")

    def interpretMov(self, line: list[Token]) -> None:
        result = self._expectTypes(
            line, [TokenType.COMMAND, TokenType.REGISTER, TokenType.REGISTER]
        )

        if not result:
            self.raiseError(
                f"Invalid command usage for 'mov'. Expected command in form 'mov <regX> <regY>'"
            )

        command, register1, register2 = line

        self._registers[register2.value] = self.getRegister(register1.value)
        self._registers[register1.value] = 0.0

    def interpretSet(self, line: list[Token]) -> None:
        result = self._expectTypes(
            line, [TokenType.COMMAND, TokenType.REGISTER, TokenType.LITERAL]
        )

        if not result:
            self.raiseError(
                f"Invalid command usage for 'set'. Expected command in form 'set <regX> <literal>'"
            )

        command, register, literal = line

        if literal.tokenValue == TokenValue.LITERAL_NUMBER:
            self._registers[register.value] = float(literal.value)
        elif literal.tokenValue == TokenValue.LITERAL_STRING:
            self._registers[register.value] = literal.value
        else:
            raise NotImplementedError("Invalid literal type.")

    def interpretCpy(self, line: list[Token]) -> None:
        result = self._expectTypes(
            line, [TokenType.COMMAND, TokenType.REGISTER, TokenType.REGISTER]
        )

        if not result:
            self.raiseError(
                f"Invalid command usage for 'cpy'. Expected command in form 'cpy <regFr> <regTo>'"
            )

        command, register1, register2 = line

        self._registers[register2.value] = self.getRegister(register1.value)

    def interpretMath(self, line: list[Token], operation: TokenValue) -> None:
        result = self._expectTypes(
            line,
            [
                TokenType.COMMAND,
                (TokenType.REGISTER, TokenType.LITERAL),
                (TokenType.REGISTER, TokenType.LITERAL),
                TokenType.REGISTER,
            ],
        )

        if not result:
            self.raiseError(
                f"Invalid usage for '{operation.name.lower()}'. Expected command in form '{operation.name.lower()} <reg|num> <reg|num> <regO>'"
            )

        command, inA, inB, register3 = line

        if inA.tokenType == TokenType.REGISTER:
            valueA = self.getRegister(inA.value)
        elif inA.tokenType == TokenType.LITERAL:
            if inA.tokenValue == TokenValue.LITERAL_NUMBER:
                valueA = inA.value
            else:
                self.raiseError(
                    f"Invalid usage for '{operation.name.lower()}'. Expected literal number, got '{inA.tokenValue}'."
                )
        else:
            raise NotImplementedError("Invalid argument type.")

        if inB.tokenType == TokenType.REGISTER:
            valueB = self.getRegister(inB.value)
        elif inB.tokenType == TokenType.LITERAL:
            if inB.tokenValue == TokenValue.LITERAL_NUMBER:
                valueB = inB.value
            else:
                self.raiseError(
                    f"Invalid usage for '{operation.name.lower()}'. Expected literal number, got '{inB.tokenValue}'."
                )
        else:
            raise NotImplementedError("Invalid argument type.")

        if operation == TokenValue.COMMAND_ADD:
            self.setRegister(register3.value, valueA + valueB)
        elif operation == TokenValue.COMMAND_SUB:
            self.setRegister(register3.value, valueA - valueB)
        elif operation == TokenValue.COMMAND_MUL:
            self.setRegister(register3.value, valueA * valueB)
        elif operation == TokenValue.COMMAND_DIV:
            self.setRegister(register3.value, valueA / valueB)
        elif operation == TokenValue.COMMAND_MOD:
            self.setRegister(register3.value, valueA % valueB)
        elif operation == TokenValue.COMMAND_POW:
            self.setRegister(register3.value, valueA**valueB)
        else:
            raise NotImplementedError("Invalid operation.")

    def interpretStdout(self, line: list[Token]) -> None:
        # Don't expect any arguments, just print everything in the line
        if len(line) == 1:
            print()
            return

        string = ""
        for token in line[1:]:
            if token.tokenType == TokenType.REGISTER:
                string += str(self.getRegister(token.value))
            elif token.tokenType == TokenType.LITERAL:
                string += str(token.value)
            elif token.tokenType == TokenType.COMMAND:
                if token.tokenValue == TokenValue.COMMAND_ENDL:
                    string += "\n"
                elif token.tokenValue == TokenValue.COMMAND_SPACE:
                    print("hisisidhisd")
                    string += " "
                else:
                    string += token.value

            elif token.tokenType == TokenType.COMPARE:
                string += token.value
            else:
                raise NotImplementedError("Invalid token type.")

        print(string, end="")

    def interpretSetJumpPoint(self, line: list[Token]) -> None:
        result = self._expectTypes(line, [TokenType.COMMAND, TokenType.LITERAL])

        if not result:
            self.raiseError(
                f"Invalid command usage for 'setjmpp'. Expected command in form 'setjmpp <string lit>'"
            )

        command, literal = line

        if literal.tokenValue != TokenValue.LITERAL_STRING:
            self.raiseError(
                f"Invalid command usage for 'setjmpp'. Expected literal string, got '{literal.tokenValue}'"
            )

        # Check for valid jump point name
        if not literal.value.isalnum():
            self.raiseError(
                f"Invalid command usage for 'setjmpp'. Jump point name must be alphanumeric."
            )

        if literal.value.lower() != literal.value:
            self.raiseError(
                f"Invalid command usage for 'setjmpp'. Jump point name must be lowercase."
            )

        if literal.value in COMMAND_MAP.keys():
            self.raiseError(
                f"Invalid command usage for 'setjmpp'. Jump point name cannot shadow built in names."
            )

        if " " in literal.value:
            self.raiseError(
                f"Invalid command usage for 'setjmpp'. Jump point name cannot contain spaces."
            )

        self._jumpPoints[literal.value] = self._lineNum

    def interpretJmp(self, line: list[Token]) -> None:
        result = self._expectTypes(line, [TokenType.COMMAND, TokenType.LITERAL])

        if not result:
            self.raiseError(
                f"Invalid command usage for 'jmp'. Expected command in form 'jmp <string lit>'"
            )

        command, literal = line

        if literal.tokenValue != TokenValue.LITERAL_STRING:
            self.raiseError(
                f"Invalid command usage for 'jmp'. Expected literal string, got '{literal.tokenValue}'"
            )

        if literal.value not in self._jumpPoints.keys():
            self.raiseError(f"Jump point '{literal.value}' does not exist.")

        self._lineNum = self._jumpPoints[literal.value]

    def interpretJmpIf(self, line: list[Token]) -> None:
        result = self._expectTypes(
            line,
            [
                TokenType.COMMAND,
                TokenType.LITERAL,
                TokenType.REGISTER,
                TokenType.COMPARE,
                (TokenType.REGISTER, TokenType.LITERAL),
            ],
        )

        if not result:
            self.raiseError(
                f"Invalid command usage for 'jmpif'. Expected command in form 'jmpif <string lit> <reg> <compare> <reg|number>'"
            )

        command, jumpPoint, arg1, compare, arg2 = line

        arg1Value = self.getRegister(arg1.value)

        if arg2.tokenType == TokenType.REGISTER:
            arg2Value = self.getRegister(arg2.value)
        elif arg2.tokenType == TokenType.LITERAL:
            if arg2.tokenValue == TokenValue.LITERAL_NUMBER:
                arg2Value = float(arg2.value)
            else:
                self.raiseError(
                    f"Invalid command usage for 'jmpif'. Expected literal number, got '{arg2.tokenValue}'."
                )
        else:
            raise NotImplementedError("Invalid argument type.")

        if jumpPoint.tokenValue != TokenValue.LITERAL_STRING:
            self.raiseError(
                f"Invalid command usage for 'jmpif'. Expected literal string, got '{jumpPoint.tokenValue}'"
            )

        if jumpPoint.value not in self._jumpPoints.keys():
            self.raiseError(f"Jump point '{jumpPoint.value}' does not exist.")

        if compare.tokenValue == TokenValue.COMPARE_EQ:
            if arg1Value == arg2Value:
                self._lineNum = self._jumpPoints[jumpPoint.value]
        elif compare.tokenValue == TokenValue.COMPARE_NEQ:
            if arg1Value != arg2Value:
                self._lineNum = self._jumpPoints[jumpPoint.value]
        elif compare.tokenValue == TokenValue.COMPARE_GT:
            if arg1Value > arg2Value:
                self._lineNum = self._jumpPoints[jumpPoint.value]
        elif compare.tokenValue == TokenValue.COMPARE_LT:
            if arg1Value < arg2Value:
                self._lineNum = self._jumpPoints[jumpPoint.value]
        elif compare.tokenValue == TokenValue.COMPARE_GTE:
            if arg1Value >= arg2Value:
                self._lineNum = self._jumpPoints[jumpPoint.value]
        elif compare.tokenValue == TokenValue.COMPARE_LTE:
            if arg1Value <= arg2Value:
                self._lineNum = self._jumpPoints[jumpPoint.value]
        else:
            raise NotImplementedError("Invalid comparison.")

    def interpretStrlen(self, line: list[Token]) -> None:
        result = self._expectTypes(
            line, [TokenType.COMMAND, TokenType.REGISTER, TokenType.REGISTER]
        )

        if not result:
            self.raiseError(
                f"Invalid command usage for 'strlen'. Expected command in form 'strlen <regIn> <regOut>'"
            )

        command, arg1, arg2 = line

        value = self.getRegister(arg1.value)

        if not isinstance(value, str):
            self.raiseError(
                f"Invalid command usage for 'strlen'. Expected string, got '{type(value)}'"
            )

        self.setRegister(arg2.value, len(value))

    def interpretStrapp(self, line: list[Token]) -> None:
        result = self._expectTypes(
            line,
            [
                TokenType.COMMAND,
                TokenType.REGISTER,
                (TokenType.REGISTER, TokenType.LITERAL),
                TokenType.REGISTER,
            ],
        )

        if not result:
            self.raiseError(
                f"Invalid command usage for 'strapp'. Expected command in form 'strapp <regIn> <reg|literal> <regOut>'"
            )

        command, arg1, arg2, arg3 = line

        value1 = self.getRegister(arg1.value)

        if not isinstance(value1, str):
            self.raiseError(
                f"Invalid command usage for 'strapp'. Expected string, got '{type(value1)}'"
            )

        if arg2.tokenType == TokenType.REGISTER:
            value2 = self.getRegister(arg2.value)
        elif arg2.tokenType == TokenType.LITERAL:
            if arg2.tokenValue == TokenValue.LITERAL_STRING:
                value2 = arg2.value
            else:
                self.raiseError(
                    f"Invalid command usage for 'strapp'. Expected string literal, got '{arg2.tokenValue}'"
                )
        else:
            raise NotImplementedError("Invalid argument type.")

        if not isinstance(value2, str):
            self.raiseError(
                f"Invalid command usage for 'strapp'. Expected string, got '{type(value2)}'"
            )

        self.setRegister(arg3.value, value1 + value2)

    def interpretCharAt(self, line: list[Token]) -> None:
        result = self._expectTypes(
            line,
            [
                TokenType.COMMAND,
                TokenType.REGISTER,
                (TokenType.REGISTER, TokenType.LITERAL),
                TokenType.REGISTER,
            ],
        )

        if not result:
            self.raiseError(
                f"Invalid command usage for 'charat'. Expected command in form 'charat <regIn> <reg|literal> <regOut>'"
            )

        command, arg1, arg2, arg3 = line

        value1 = self.getRegister(arg1.value)

        if not isinstance(value1, str):
            self.raiseError(
                f"Invalid command usage for 'charat'. Expected string, got '{type(value1)}'"
            )

        if arg2.tokenType == TokenType.REGISTER:
            value2 = self.getRegister(arg2.value)
        elif arg2.tokenType == TokenType.LITERAL:
            if arg2.tokenValue == TokenValue.LITERAL_NUMBER:
                value2 = int(arg2.value)
            else:
                self.raiseError(
                    f"Invalid command usage for 'charat'. Expected number literal, got '{arg2.tokenValue}'"
                )
        else:
            raise NotImplementedError("Invalid argument type.")

        if not isinstance(value2, float):
            self.raiseError(
                f"Invalid command usage for 'charat'. Expected number, got '{type(value2)}'"
            )

        value2 = int(value2)

        if value2 < 0 or value2 >= len(value1):
            self.raiseError(f"Invalid command usage for 'charat'. Index out of bounds.")

        char = value1[value2]

        self.setRegister(arg3.value, char)

    def _expectTypes(
        self, line: list[Token], types: list[TokenType | tuple[TokenType]]
    ) -> bool:
        if len(line) != len(types):
            return False

        for expectedType, token in zip(types, line):
            if isinstance(expectedType, tuple):
                if token.tokenType not in expectedType:
                    return False
                continue

            if token.tokenType != expectedType:
                return False

        return True

    def raiseError(self, message: str) -> None:
        print(f"Error on line {self._lineNum}:")
        print(f" - {message}")
        print(f' - LINE: "{self._recreateLine(self._currentLine)}"')
        print(f" - TOKENS: {self._formatTokenList(self._currentLine)}")
        exit(1)

    def getRegister(self, register: str) -> float:
        if register not in self._registers:
            # Create register
            self._registers[register] = 0.0

        return self._registers[register]

    def setRegister(self, register: str, value: float) -> None:
        assert isinstance(register, str)
        self._registers[register] = value
