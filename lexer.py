from typing import Union

from enums import TokenType
from errors import LexerError
from tokens import Token, build_reserved_keywords

RESERVED_KEYWORDS = build_reserved_keywords()


class Lexer(object):
    def __init__(self, text: str):
        self.text: str = text
        self.pos: int = 0
        self.current_char: Union[str, None] = self.text[self.pos]

        self.lineno = 1
        self.column = 1

    def error(self):
        s = "Lexer error on '{lexeme}' line: {lineno} column: {column}".format(
            lexeme=self.current_char,
            lineno=self.lineno,
            column=self.column,
        )
        raise LexerError(message=s)

    def _id(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        token = RESERVED_KEYWORDS.get(result)
        if token is None:
            token = Token(TokenType.ID, result, lineno=self.lineno, column=self.column)
            print(token)
            return token
        token = Token(token, result, lineno=self.lineno, column=self.column)
        print(token)
        return token

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def advance(self):
        if self.current_char == '\n':
            self.lineno += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer(),
                             lineno=self.lineno, column=self.column)

            try:
                token_type = TokenType(self.current_char)
            except ValueError:
                self.error()
            else:
                token = Token(
                    token_type=token_type,
                    value=token_type.value,
                    lineno=self.lineno,
                    column=self.column
                )
                self.advance()
                print(token)
                return token
        return Token(TokenType.EOF, None)
