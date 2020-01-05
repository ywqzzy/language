from lexer import Lexer
from syntax_parser import Parser
from interpreter import *
from context import *
from symbol_table import *
from constants import *
from buildin_function import *

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("TRUE", Number.true)
global_symbol_table.set("FALSE", Number.false)
global_symbol_table.set("阴", Number.false)
global_symbol_table.set("阳", Number.true)
global_symbol_table.set("MATH_PI", Number.math_PI)
global_symbol_table.set("PRINT", BuildInFunction.print) 
global_symbol_table.set("书之", BuildInFunction.print) 
global_symbol_table.set("INPUT", BuildInFunction.input)
global_symbol_table.set("INPUT_INT", BuildInFunction.input_int)
global_symbol_table.set("CLEAR",  BuildInFunction.clear)
global_symbol_table.set("IS_NUMBER",  BuildInFunction.is_number)
global_symbol_table.set("IS_STRING",  BuildInFunction.is_string)
global_symbol_table.set("IS_LIST",  BuildInFunction.is_list)
global_symbol_table.set("IS_FUNCTION",  BuildInFunction.is_function)
global_symbol_table.set("APPEND",  BuildInFunction.append)
global_symbol_table.set("POP",  BuildInFunction.pop)
global_symbol_table.set("EXTEND",  BuildInFunction.extend)
global_symbol_table.set("LEN",  BuildInFunction.len)
global_symbol_table.set("RUN",  BuildInFunction.run)



#TODO ADD MORE CHINESE


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