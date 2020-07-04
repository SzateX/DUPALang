import ast
from typing import Any

from dupa_collections import CallStack
from enums import VariableTypes, ARType
from errors import ReturnedValue
from nodes import Compound, Declaration, DupaCall
from dupa_parser import Parser
from containers import ActivationRecord


class Interpreter(ast.NodeVisitor):
    def __init__(self, parser: Parser):
        self.parser = parser
        self.call_stack = CallStack()

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        if isinstance(node.op, ast.Add):
            return self.visit(node.left) + self.visit(node.right)
        if isinstance(node.op, ast.Sub):
            return self.visit(node.left) - self.visit(node.right)
        if isinstance(node.op, ast.Mult):
            return self.visit(node.left) * self.visit(node.right)
        if isinstance(node.op, ast.Div):
            return self.visit(node.left) / self.visit(node.right)

    def visit_Num(self, node: ast.Num) -> Any:
        return node.n

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        if isinstance(node.op, ast.UAdd):
            return +self.visit(node.operand)
        if isinstance(node.op, ast.USub):
            return -self.visit(node.operand)

    def visit_Compound(self, node: Compound):
        for child in node.body:
            self.visit(child)

    def visit_Module(self, node: ast.Module) -> Any:
        ar = ActivationRecord(
            name="program",
            type_of=ARType.PROGRAM,
            nesting_level=1
        )

        self.call_stack.push(ar)

        for child in node.body:
            self.visit(child)
        print(self.call_stack)
        self.call_stack.pop()

    def visit_Pass(self, node: ast.Pass) -> Any:
        pass

    def visit_Assign(self, node: ast.Assign) -> Any:
        var_name = node.targets[0].id
        ar = self.call_stack.peek()
        ar[var_name] = self.visit(node.value)

    def visit_Declaration(self, node: Declaration) -> Any:
        var_name = node.id
        ar = self.call_stack.peek()
        if node.type == VariableTypes.UNIVERSAL:
            ar[var_name] = None
        elif node.type == VariableTypes.INTEGER:
            ar[var_name] = 0
        elif node.type == VariableTypes.FLOAT:
            ar[var_name] = 0.0

    def visit_Name(self, node: ast.Name) -> Any:
        var_name = node.id
        ar = self.call_stack.peek()
        return ar.get(var_name)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        pass

    def visit_DupaCall(self, node: DupaCall) -> Any:
        proc_name = node.func.id
        ar = ActivationRecord(
            name=proc_name,
            type_of=ARType.PROCEDURE,
            nesting_level=node.proc_symbol.scope_level + 1
        )
        proc_symbol = node.proc_symbol
        formal_params = proc_symbol.params
        actual_params = node.args

        for param_symbol, argument_node in zip(formal_params, actual_params):
            ar[param_symbol.name] = self.visit(argument_node)

        self.call_stack.push(ar)
        print(type(proc_symbol.body))
        try:
            self.visit(proc_symbol.body)
        except ReturnedValue:
            return_value = ar.return_value
            if proc_symbol.returns is None:
                raise RuntimeError("Unexpected return")
        else:
            if proc_symbol.returns is not None:
                raise RuntimeError("Return not found")
        self.call_stack.pop()
        return return_value

    def visit_Return(self, node: ast.Return) -> Any:
        self.call_stack.peek().return_value = self.visit(node.value)
        raise ReturnedValue()

    def visit_If(self, node: ast.If) -> Any:
        if self.visit(node.test):
            return self.visit(node.body)
        elif node.orelse is not None:
            return self.visit(node.orelse)

    def interpret(self, tree=None):
        if tree is None:
            tree = self.parser.parse()
        return self.visit(tree)
