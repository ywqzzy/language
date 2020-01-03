from lexer import Lexer
from syntax_parser import Parser
from interpreter import *
from context import *
from symbol_table import *
from constants import *

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number(0))
global_symbol_table.set("TRUE", Number(1))
global_symbol_table.set("FALSE", Number(0))


def run(file_name, text):
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()

    if error: return None, error

    if tokens[0].type == TT_EOF:
        return None, None

    parser = Parser(tokens)
    ast = parser.parse()

    if ast.error: return None, ast.error

    interpreter = Interpreter()
    
    context = Context('<program>')
    context.symbol_table = global_symbol_table

    result = interpreter.visit(ast.node, context)


    return result.value, result.error