from analyzer import SemanticAnalyzer
from interpreter import Interpreter
from lexer import Lexer
from dupa_parser import Parser
from pprint import pprint

text = """def int f()
{
    return 2 + 2 * 2;
    return 0;
}
int x;
x = f();
"""


def main():
    while True:
        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.visit(tree)
        interpreter = Interpreter(parser)
        result = interpreter.interpret(tree)
        pprint(interpreter.call_stack)
        break


if __name__ == '__main__':
    main()
