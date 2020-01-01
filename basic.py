from lexer import Lexer
from syntax_parser import Parser
from interpreter import *


def run(file_name, text):
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    parser = Parser(tokens)
    ast = parser.parse()

    if ast.error: return None, ast.error

    interpreter = Interpreter()

    result = interpreter.visit(ast.node)


    return result.value, result.error