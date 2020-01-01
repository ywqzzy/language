from lexer import Lexer
from syntax_parser import Parser


def run(file_name, text):
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error