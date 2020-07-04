from typing import Union

from enums import VariableTypes


class Symbol(object):
    def __init__(self, name: str, symbol_type=None):
        self.name = name
        self.type = symbol_type
        self.scope_level = 0


class BuiltinTypeSymbol(Symbol):
    def __init__(self, name: str):
        super(BuiltinTypeSymbol, self).__init__(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')"


class VarSymbol(Symbol):
    def __init__(self, name: str, symbol_type):
        super(VarSymbol, self).__init__(name, symbol_type)

    def __str__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', type='{self.type}')>"

    def __repr__(self):
        return self.__str__()


class ProcedureSymbol(Symbol):
    def __init__(self, name, params=None, body_ast=None, returns=None):
        super(ProcedureSymbol, self).__init__(name)
        self.params = params if params is not None else []
        self.body = body_ast
        self.returns = returns

    def __str__(self):
        return f'<{self.__class__.__name__}(name={self.name}, parameters={self.params})>'

    def __repr__(self):
        return self.__str__()


class ScopedSymbolTable(object):
    def __init__(self, scope_name: str, scope_level: int,
                 enclosing_scope: Union['ScopedSymbolTable', None] = None):
        self._symbols = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope
        self._init_builtins()

    def _init_builtins(self):
        self.define(BuiltinTypeSymbol(str(VariableTypes.UNIVERSAL)))
        self.define(BuiltinTypeSymbol(str(VariableTypes.FLOAT)))
        self.define(BuiltinTypeSymbol(str(VariableTypes.INTEGER)))

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
                ('Scope name', self.scope_name),
                ('Scope level', self.scope_level),
                ('Enclosing scope',
                 self.enclosing_scope.scope_name if self.enclosing_scope else None
                 )
        ):
            lines.append('%-15s: %s' % (header_name, header_value))
        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        return '\n'.join(lines)

    def __repr__(self):
        return self.__str__()

    def define(self, symbol: Symbol):
        print(f"Define: {symbol}")
        symbol.scope_level = self.scope_level
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str, current_scope_only: bool = False):
        print(f"Lookup: {name}")
        symbol = self._symbols.get(name)
        if symbol is not None:
            return symbol

        if current_scope_only:
            return None

        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)
