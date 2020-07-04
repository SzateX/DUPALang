import ast


class Compound(ast.stmt):
    # no doc
    # noinspection PyMissingConstructor
    def __init__(self, *args, **kwargs):  # real signature unknown
        if len(args) > 0:
            self.body = args[0]
        if 'body' in kwargs:
            self.body = kwargs['body']

    _fields = (
        'body',
    )


class VariableStructure(ast.stmt):
    # no doc
    # noinspection PyMissingConstructor
    def __init__(self, *args, **kwargs):  # real signature unknown
        if len(args) > 0:
            self.id = args[0]
            self.type = args[1]
        if 'body' in kwargs:
            self.body = kwargs['id']
            self.type = kwargs['type']

    _fields = (
        'id',
        'type'
    )


class Declaration(VariableStructure):
    pass


class Param(VariableStructure):
    pass


class DupaCall(ast.expr):
    def __init__(self, func, args=None, keywords=None, proc_symbol=None):
        super(DupaCall, self).__init__()
        self.func = func
        self.args = args
        self.keywords = keywords
        self.proc_symbol = proc_symbol
