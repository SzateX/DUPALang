from analyzer import SemanticAnalyzer
from interpreter import Interpreter
from lexer import Lexer
from dupa_parser import Parser
from pprint import pprint

text = """def int f()
{
    return 2 + 2 * 2;
}

def int g()
{
    return 15;
}
int x;
int y;
x = 0;
if(x) y = 10;
else
{
    y = 50;
}    
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
