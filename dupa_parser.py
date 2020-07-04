import ast
from typing import Union

from enums import ErrorCode, TokenType, VariableTypes
from errors import ParserError
from nodes import Compound, Declaration, Param, DupaCall, IterFor, DoWhile
from tokens import Token


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token: Union[Token, None] = self.lexer.get_next_token()

    def error(self, error_code: ErrorCode, token: Token):
        print(str(error_code))
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f'{str(error_code.value)} -> {str(token)}',
        )

    def eat(self, token_type):
        if self.current_token.token_type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )

    def program(self):
        """program: statement_list"""
        nodes = self.statement_list()
        return ast.Module(body=nodes)

    def statement_list(self):
        """statement_list: statement
                         | compound_statement
                         | function_definition
                         | statement SEMI statement_list
                         | compound_statement statement_list
                         | function_definition statement_list"""
        if self.current_token.token_type == TokenType.LBR:
            return [self.compound_statement()] + self.statement_list()
        if self.current_token.token_type == TokenType.DEF:
            return [self.function_definition()] + self.statement_list()
        node = self.statement()
        if self.current_token.token_type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
            return [node] + self.statement_list()
        else:
            return [node]

    def compound_statement(self):
        """compound_statement: LBR statement_list RBR"""
        self.eat(TokenType.LBR)
        nodes = self.statement_list()
        self.eat(TokenType.RBR)

        root = Compound(nodes)
        return root

    def statement(self):
        """statement: assigment_statement
                    | declaration_statement
                    | empty
                    | proccall_statement
                    | return_statement
                    | break_statement
                    | continue_statement
                    | conditional_statement
                    | loop_statement"""
        if self.current_token.token_type == TokenType.ID and self.lexer.current_char == '(':
            return self.proccall_statement()
        if self.current_token.token_type == TokenType.ID:
            return self.assigment_statement()
        if self.current_token.token_type in (
                TokenType.VAR, TokenType.INT, TokenType.FLOAT):
            return self.declaration_statement()
        if self.current_token.token_type == TokenType.RETURN:
            return self.return_statement()
        if self.current_token.token_type == TokenType.IF:
            return self.conditional_statement()
        if self.current_token.token_type in (TokenType.FOR, TokenType.WHILE, TokenType.DO):
            return self.loop_statement()
        if self.current_token.token_type == TokenType.BREAK:
            return self.break_statement()
        if self.current_token.token_type == TokenType.CONTINUE:
            return self.continue_statement()
        return self.empty()

    def function_definition(self):
        """function_definition:
        DEF (INT | FLOAT | VAR | empty) ID LPAR arguments RPAR compound_statement"""
        self.eat(TokenType.DEF)
        if self.current_token.token_type == TokenType.INT:
            return_type = VariableTypes.INTEGER
            self.eat(TokenType.INT)
        elif self.current_token.token_type == TokenType.FLOAT:
            return_type = VariableTypes.FLOAT
            self.eat(TokenType.FLOAT)
        elif self.current_token.token_type == TokenType.VAR:
            return_type = VariableTypes.UNIVERSAL
            self.eat(TokenType.VAR)
        else:
            return_type = None
        name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.LPAR)
        arguments = self.arguments()
        self.eat(TokenType.RPAR)
        body = self.compound_statement()
        return ast.FunctionDef(name=name, args=arguments, body=body, returns=return_type)

    def arguments(self):
        """arguments: empty | argument | argument COMMA arguments"""
        if self.current_token.token_type == TokenType.RPAR:
            return []
        else:
            args = [self.argument()]
            if self.current_token.token_type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args += self.arguments()
            return args

    def argument(self):
        """argument: (INT | FLOAT | VAR) ID"""
        if self.current_token.token_type == TokenType.VAR:
            self.eat(TokenType.VAR)
            node = Param(self.current_token.value, VariableTypes.UNIVERSAL)
        elif self.current_token.token_type == TokenType.INT:
            self.eat(TokenType.INT)
            node = Param(self.current_token.value, VariableTypes.INTEGER)
        elif self.current_token.token_type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
            node = Param(self.current_token.value, VariableTypes.FLOAT)
        else:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN,
                       token=self.current_token)
        self.eat(TokenType.ID)
        return node

    def assigment_statement(self):
        """assigment_statement: variable ASSIGN expr"""
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASSIGN)
        right = self.expr()
        node = ast.Assign([left], right)
        return node

    def declaration_statement(self):
        """declaration_statement: (INT | FLOAT | VAR) ID"""
        if self.current_token.token_type == TokenType.VAR:
            self.eat(TokenType.VAR)
            node = Declaration(self.current_token.value,
                               VariableTypes.UNIVERSAL)
        elif self.current_token.token_type == TokenType.INT:
            self.eat(TokenType.INT)
            node = Declaration(self.current_token.value, VariableTypes.INTEGER)
        elif self.current_token.token_type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
            node = Declaration(self.current_token.value, VariableTypes.FLOAT)
        else:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN,
                       token=self.current_token)
        self.eat(TokenType.ID)
        return node

    def variable(self):
        """variable: ID"""
        node = ast.Name(self.current_token.value)
        self.eat(TokenType.ID)
        return node

    def expr(self):
        """expr: term ((PLUS | MINUS) term)*"""
        node = self.term()

        while self.current_token.token_type in (
                TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            op = None
            if token.token_type == TokenType.PLUS:
                op = ast.Add()
                self.eat(TokenType.PLUS)
            elif token.token_type == TokenType.MINUS:
                op = ast.Sub()
                self.eat(TokenType.MINUS)

            node = ast.BinOp(node, op, self.term())

        return node

    def term(self):
        """term: factor ((MUL | DIV) factor)*"""
        node = self.factor()
        while self.current_token.token_type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            op = None
            if token.token_type == TokenType.MUL:
                op = ast.Mult()
                self.eat(TokenType.MUL)
            elif token.token_type == TokenType.DIV:
                op = ast.Div()
                self.eat(TokenType.DIV)

            node = ast.BinOp(node, op, self.factor())

        return node

    def factor(self):
        """factor: (PLUS | MINUS) factor
                 | INTEGER
                 | LPAREN expr RPAREN
                 | proccall_statement
                 | variable"""
        token = self.current_token
        if token.token_type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            node = ast.UnaryOp(ast.UAdd(), self.factor())
            return node
        if token.token_type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            node = ast.UnaryOp(ast.USub(), self.factor())
            return node
        if token.token_type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return ast.Num(token.value)
        if token.token_type == TokenType.LPAR:
            self.eat(TokenType.LPAR)
            node = self.expr()
            self.eat(TokenType.RPAR)
            return node
        if token.token_type == TokenType.ID and self.lexer.current_char == "(":
            return self.proccall_statement()
        else:
            return self.variable()

    def empty(self):
        """empty: NOTHING"""
        return ast.Pass()

    def proccall_statement(self):
        """proccall_statement: ID LPAR (expr + [COMMA expr]*)? RPAR"""
        token = self.current_token

        proc_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.LPAR)
        actual_params = []
        if self.current_token.token_type != TokenType.RPAR:
            node = self.expr()
            actual_params.append(node)

        while self.current_token.token_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            node = self.expr()
            actual_params.append(node)

        self.eat(TokenType.RPAR)

        node = DupaCall(func=ast.Name(proc_name), args=actual_params)
        return node

    def return_statement(self):
        """return_statement: RETURN expr"""
        self.eat(TokenType.RETURN)
        return ast.Return(value=self.expr())

    def conditional_statement(self):
        """conditional_statement: if LPAR expr RPAR (statement SEMI | compound_statement) (else (statement SEMI | compund_statement))?"""
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAR)
        expr = self.expr()
        self.eat(TokenType.RPAR)
        if self.current_token.token_type == TokenType.LBR:
            body = self.compound_statement()
        else:
            body = self.statement()
            self.eat(TokenType.SEMI)
        else_body = None
        if self.current_token.token_type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            if self.current_token.token_type == TokenType.LBR:
                else_body = self.compound_statement()
            else:
                else_body = self.statement()
                self.eat(TokenType.SEMI)
        return ast.If(test=expr, body=body, orelse=else_body)

    def loop_statement(self):
        """loop_statement: for_statement | while_statement | do_while_statement"""
        if self.current_token.token_type == TokenType.FOR:
            return self.for_statement()
        elif self.current_token.token_type == TokenType.WHILE:
            return self.while_statement()
        elif self.current_token.token_type == TokenType.DO:
            return self.do_while_statement()

    def for_statement(self):
        """for_statement: FOR LPAR statement SEMI EXPR SEMI statement RPAR (statement SEMI | compound_statement)"""
        self.eat(TokenType.FOR)
        self.eat(TokenType.LPAR)
        expr1 = self.statement()
        self.eat(TokenType.SEMI)
        expr2 = self.expr()
        self.eat(TokenType.SEMI)
        expr3 = self.statement()
        self.eat(TokenType.RPAR)
        if self.current_token.token_type == TokenType.LBR:
            body = self.compound_statement()
        else:
            body = self.statement()
            self.eat(TokenType.SEMI)
        return IterFor(expr1, expr2, expr3, body)

    def while_statement(self):
        """while_statement: WHILE LPAR EXPR RPAR (statement SEMI | compound_statement)"""
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAR)
        expr = self.expr()
        self.eat(TokenType.RPAR)
        if self.current_token.token_type == TokenType.LBR:
            body = self.compound_statement()
        else:
            body = self.statement()
            self.eat(TokenType.SEMI)
        return ast.While(test=expr, body=body)

    def do_while_statement(self):
        """DO (statement SEMI | compound_statement) WHILE LPAR expr RPAR SEMI"""
        self.eat(TokenType.DO)
        if self.current_token.token_type == TokenType.LBR:
            body = self.compound_statement()
        else:
            body = self.statement()
            self.eat(TokenType.SEMI)
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAR)
        expr = self.expr()
        self.eat(TokenType.RPAR)
        self.eat(TokenType.SEMI)
        return DoWhile(expr, body)

    def continue_statement(self):
        """continue_statement: CONTINUE"""
        self.eat(TokenType.CONTINUE)
        return ast.Continue()

    def break_statement(self):
        """break_statement: BREAK"""
        self.eat(TokenType.BREAK)
        return ast.Break()

    def parse(self):
        node = self.program()
        if self.current_token.token_type != TokenType.EOF:
            print(self.current_token.value)
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN,
                       token=self.current_token)
        return node
