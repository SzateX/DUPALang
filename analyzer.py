import ast
from typing import Any, Union

from enums import ErrorCode
from errors import SemanticError
from nodes import Compound, Declaration, DupaCall
from symbols import ScopedSymbolTable, ProcedureSymbol, VarSymbol


class SemanticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.current_scope: Union[ScopedSymbolTable, None] = None

    def error(self, error_code, token):
        raise SemanticError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}'
        )

    def visit_Module(self, node: ast.Module) -> Any:
        print('ENTER scope: global')
        global_scope = ScopedSymbolTable(scope_name='global', scope_level=1,
                                         enclosing_scope=self.current_scope)
        self.current_scope = global_scope
        for child in node.body:
            self.visit(child)

        print(global_scope)
        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: global')

    def visit_Pass(self, node: ast.Pass) -> Any:
        pass

    def visit_DupaCall(self, node: DupaCall) -> Any:
        proc_symbol: ProcedureSymbol = self.current_scope.lookup(node.func.id)
        if len(proc_symbol.params) != len(node.args):
            self.error(error_code=ErrorCode.WRONG_PARAM_NUM, token=node)
        for param_node in node.args:
            self.visit(param_node)
        node.proc_symbol = proc_symbol

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        name = node.name
        proc_symbol = ProcedureSymbol(name)
        self.current_scope.define(proc_symbol)

        print("ENTER scope: %s" % name)
        procedure_scope = ScopedSymbolTable(scope_name=name,
                                            scope_level=self.current_scope.scope_level + 1,
                                            enclosing_scope=self.current_scope)
        self.current_scope = procedure_scope

        for param in node.args:
            param_type = self.current_scope.lookup(param.type)
            param_name = param.id
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.define(var_symbol)
            proc_symbol.params.append(var_symbol)

        self.visit(node.body)
        print(procedure_scope)
        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: %s' % name)
        proc_symbol.body = node.body
        proc_symbol.returns = node.returns

    def visit_Compound(self, node: Compound):
        for child in node.body:
            self.visit(child)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        self.visit(node.operand)

    def visit_Num(self, node: ast.Num) -> Any:
        pass

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        self.visit(node.left)
        self.visit(node.right)

    def visit_Declaration(self, node: Declaration):
        type_name = node.type
        type_symbol = self.current_scope.lookup(type_name)
        var_name = node.id
        var_symbol = VarSymbol(var_name, type_symbol)

        if self.current_scope.lookup(var_name, current_scope_only=True):
            self.error(error_code=ErrorCode.DUPLICATE_ID, token=var_name)
            raise Exception(f"Duplicate identifier {var_name} found")

        self.current_scope.define(var_symbol)

    def visit_Assign(self, node: ast.Assign) -> Any:
        var_name = node.targets[0].id
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))
        self.visit(node.value)

    def visit_Name(self, node: ast.Name) -> Any:
        var_name = node.id
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            self.error(error_code=ErrorCode.IDENTIFIER_NOT_FOUND,
                       token=var_name)