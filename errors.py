from enums import ErrorCode
from tokens import Token


class ReturnedValue(Exception):
    pass


class ContinueIteration(Exception):
    pass


class PreInterpretError(Exception):
    def __init__(self, error_code: ErrorCode = None, token: Token = None,
                 message=None):
        self.error_code = error_code
        self.token = token
        super(PreInterpretError, self).__init__(message)


class LexerError(PreInterpretError):
    pass


class ParserError(PreInterpretError):
    pass


class SemanticError(PreInterpretError):
    pass
