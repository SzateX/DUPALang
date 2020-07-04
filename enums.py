from enum import Enum


class TokenType(Enum):
    # Token types
    #
    # EOF (end-of-file) token is used to indicate that
    # there is no more input left for lexical analysis

    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    LPAR = '('
    RPAR = ')'
    ASSIGN = '='
    SEMI = ';'
    DOT = '.'
    LBR = '{'
    RBR = '}'
    COMMA = ','
    # RESERVED TOKENS
    VAR = 'var'
    INT = 'int'
    FLOAT = 'float'
    RETURN = 'return'
    IF = 'if'
    ELSE = 'else'
    DEF = 'def'
    # OTHER
    INTEGER = 'INTEGER'
    ID = 'ID'
    EOF = 'EOF'


class ErrorCode(Enum):
    UNEXPECTED_TOKEN = 'Unexpected token'
    IDENTIFIER_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate identifier found'
    WRONG_PARAM_NUM = 'Wrong number of parameters'


class VariableTypes(Enum):
    UNIVERSAL = 'UNIVERSAL'
    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'


class ARType(Enum):
    PROGRAM = 'PROGRAM'
    PROCEDURE = 'PROCEDURE'