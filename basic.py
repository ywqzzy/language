from lexer import Lexer
from syntax_parser import Parser
from interpreter import *
from context import *
from symbol_table import *

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))


def run(file_name, text):
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    parser = Parser(tokens)
    ast = parser.parse()

    if ast.error: return None, ast.error

    interpreter = Interpreter()
    
    context = Context('<program>')
    context.symbol_table = global_symbol_table

    result = interpreter.visit(ast.node, context)


    return result.value, result.error