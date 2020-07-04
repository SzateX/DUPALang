from typing import Any

from enums import TokenType


class Token(object):
    def __init__(self, token_type: TokenType, value: Any, lineno: int = None,
                 column: int = None):
        self.token_type = token_type
        self.value = value
        self.lineno = lineno
        self.column = column

    def __str__(self):
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.token_type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column
        )

    def __repr__(self):
        return self.__str__()


def build_reserved_keywords():
    tt_list = list(TokenType)
    start_index = tt_list.index(TokenType.VAR)
    end_index = tt_list.index(TokenType.DEF)
    return {
        token_type.value: token_type
        for token_type in tt_list[start_index:end_index + 1]
    }
