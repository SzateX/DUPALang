import ast
import inspect
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
        print("BEGIN PRORGRAM")
        nodes = self.statement_list()
        print("END PRGORAM")
        return ast.Module(body=nodes)

    def statement_list(self):
        """statement_list: statement
                         | compound_statement
                         | function_definition
                         | statement statement_list
                         | compound_statement statement_list
                         | function_definition statement_list
                         | nothing"""
        print("BEGIN statement_list")
        nodes = []
        if self.current_token.token_type == TokenType.LBR:
            nodes += [self.compound_statement()] + self.statement_list()
        elif self.current_token.token_type == TokenType.DEF:
            nodes += [self.function_definition()] + self.statement_list()
        elif self.current_token.token_type in (TokenType.RBR, TokenType.EOF):
            pass
        else:
            node = self.statement()
            # if self.current_token.token_type == TokenType.SEMI:
            #     self.eat(TokenType.SEMI)
            nodes += [node] + self.statement_list()
            #else:
            #    nodes += [node]
        print("END statement_list")
        return nodes

    def compound_statement(self):
        """compound_statement: LBR statement_list RBR"""
        print("BEGIN compound_statement")
        self.eat(TokenType.LBR)
        nodes = self.statement_list()
        self.eat(TokenType.RBR)

        root = Compound(nodes)
        print("END compound_statement")
        return root

    def statement(self):
        """statement: assigment_statement SEMI
                    | declaration_statement SEMI
                    | empty
                    | proccall_statement SEMI
                    | return_statement SEMI
                    | break_statement SEMI
                    | continue_statement SEMI
                    | conditional_statement
                    | loop_statement"""
        print("BEGIN statement")
        node = None
        if self.current_token.token_type == TokenType.ID and self.lexer.current_char == '(':
            node = self.proccall_statement()
        elif self.current_token.token_type == TokenType.ID:
            node = self.assigment_statement()
            self.eat(TokenType.SEMI)
        elif self.current_token.token_type in (
                TokenType.VAR, TokenType.INT, TokenType.FLOAT):
            node = self.declaration_statement()
            self.eat(TokenType.SEMI)
        elif self.current_token.token_type == TokenType.RETURN:
            node = self.return_statement()
            self.eat(TokenType.SEMI)
        elif self.current_token.token_type == TokenType.IF:
            node = self.conditional_statement()
        elif self.current_token.token_type in (TokenType.FOR, TokenType.WHILE, TokenType.DO):
            node = self.loop_statement()
        elif self.current_token.token_type == TokenType.BREAK:
            node = self.break_statement()
            self.eat(TokenType.SEMI)
        elif self.current_token.token_type == TokenType.CONTINUE:
            node = self.continue_statement()
            self.eat(TokenType.SEMI)
        else:
            node = self.empty()
        print("END statement")
        return node

    def function_definition(self):
        """function_definition:
        DEF (INT | FLOAT | VAR | empty) ID LPAR arguments RPAR compound_statement"""
        print("BEGIN function_definition")
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
        print("END function_definition")
        return ast.FunctionDef(name=name, args=arguments, body=body, returns=return_type)

    def arguments(self):
        """arguments: empty | argument | argument COMMA arguments"""
        print("BEGIN arguments")
        if self.current_token.token_type == TokenType.RPAR:
            print("END arguments")
            return []
        else:
            args = [self.argument()]
            if self.current_token.token_type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args += self.arguments()
            print("END arguments")
            return args

    def argument(self):
        """argument: (INT | FLOAT | VAR) ID"""
        print("BEGIN argument")
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
        print("END argument")
        return node

    def assigment_statement(self):
        """assigment_statement: variable ASSIGN expr"""
        print("BEGIN assigment_statement")
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASSIGN)
        right = self.expr()
        node = ast.Assign([left], right)
        print("END assigment_statement")
        return node

    def declaration_statement(self):
        """declaration_statement: (INT | FLOAT | VAR) ID"""
        print("BEGIN declaration_statement")
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
        print("END declaration_statement")
        return node

    def variable(self):
        """variable: ID"""
        print("BEGIN variable")
        node = ast.Name(self.current_token.value)
        self.eat(TokenType.ID)
        print("END variable")
        return node

    def expr(self):
        """expr: term ((PLUS | MINUS) term)*"""
        print("BEGIN expr")
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
        print("END expr")
        return node

    def term(self):
        """term: factor ((MUL | DIV) factor)*"""
        print("BEGIN term")
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
        print("END term")
        return node

    def factor(self):
        """factor: (PLUS | MINUS) factor
                 | INTEGER
                 | LPAREN expr RPAREN
                 | proccall_statement
                 | variable"""
        print("BEGIN factor")
        token = self.current_token
        node = None
        if token.token_type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            node = ast.UnaryOp(ast.UAdd(), self.factor())
        elif token.token_type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            node = ast.UnaryOp(ast.USub(), self.factor())
        elif token.token_type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            node = ast.Num(token.value)
        elif token.token_type == TokenType.LPAR:
            self.eat(TokenType.LPAR)
            node = self.expr()
            self.eat(TokenType.RPAR)
        elif token.token_type == TokenType.ID and self.lexer.current_char == "(":
            node = self.proccall_statement()
        else:
            node = self.variable()
        print("END factor")
        return node

    def empty(self):
        """empty: NOTHING"""
        print("BEGIN empty")
        print("END empty")
        return ast.Pass()

    def proccall_statement(self):
        """proccall_statement: ID LPAR (expr + [COMMA expr]*)? RPAR"""
        print("BEGIN proccall_statement")
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
        print("END proccall_statement")
        return node

    def return_statement(self):
        """return_statement: RETURN expr"""
        print("BEGIN return_statement")
        self.eat(TokenType.RETURN)
        print("END return_statement")
        return ast.Return(value=self.expr())

    def conditional_statement(self):
        """conditional_statement: if LPAR expr RPAR (statement SEMI | compound_statement) (else (statement SEMI | compund_statement))?"""
        print("BEGIN conditional_statement")
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
        print("END conditional_statement")
        return ast.If(test=expr, body=body, orelse=else_body)

    def loop_statement(self):
        """loop_statement: for_statement | while_statement | do_while_statement"""
        print("BEGIN loop_statement")
        node = None
        if self.current_token.token_type == TokenType.FOR:
            node = self.for_statement()
        elif self.current_token.token_type == TokenType.WHILE:
            node = self.while_statement()
        elif self.current_token.token_type == TokenType.DO:
            node = self.do_while_statement()
        print("END loop_statement")
        return node

    def for_statement(self):
        """for_statement: FOR LPAR statement SEMI EXPR SEMI statement RPAR (statement SEMI | compound_statement)"""
        print("BEGIN for_statement")
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
        print("END for_statement")
        return IterFor(expr1, expr2, expr3, body)

    def while_statement(self):
        """while_statement: WHILE LPAR EXPR RPAR (statement SEMI | compound_statement)"""
        print("BEGIN while_statement")
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAR)
        expr = self.expr()
        self.eat(TokenType.RPAR)
        if self.current_token.token_type == TokenType.LBR:
            body = self.compound_statement()
        else:
            body = self.statement()
            self.eat(TokenType.SEMI)
        print("END while_statement")
        return ast.While(test=expr, body=body)

    def do_while_statement(self):
        """DO (statement SEMI | compound_statement) WHILE LPAR expr RPAR SEMI"""
        print("BEGIN do_while_statement")
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
        print("END do_while_statement")
        return DoWhile(expr, body)

    def continue_statement(self):
        """continue_statement: CONTINUE"""
        print("BEGIN continue_statement")
        self.eat(TokenType.CONTINUE)
        print("END continue_statement")
        return ast.Continue()

    def break_statement(self):
        """break_statement: BREAK"""
        print("BEGIN break_statement")
        self.eat(TokenType.BREAK)
        print("END break_statement")
        return ast.Break()

    def parse(self):
        node = self.program()
        if self.current_token.token_type != TokenType.EOF:
            print(self.current_token.value)
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN,
                       token=self.current_token)
        return node

    def get_grammar(self):
        object_methods = [method_name for method_name in dir(self)
                          if callable(getattr(self, method_name)) and method_name not in ("parse", "eat", "error", "get_grammar") and not method_name.startswith("__")]
        doc_strings = []
        for object_method in map(lambda x: getattr(self, x), object_methods):
            if not inspect.isbuiltin(object_method):
                doc_strings.append(inspect.getdoc(object_method))
        return "\n".join(doc_strings)
