from base_function import *
from runtime_result import RTResult
from symbol_table import *
from number_value import *
from string_value import String
from list_value import *
from error import RTError

import os

from lexer import Lexer
from syntax_parser import Parser
from interpreter import *
from context import *


class BuildInFunction(BaseFunction):

    def __init__(self, name):
        super().__init__(name)
    
    def execute(self, args):
        res = RTResult()

        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'

        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return(): return res

        return_value = res.register(method(exec_ctx))
        if res.should_return(): return res

        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')
    
    def copy(self):
        copy = BuildInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __expr__(self):
        return f'<built-in function {self.name}>'

    
    def  execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return RTResult().success(Number.null)
    execute_print.arg_names = ['value']
    
    def execute_print_ret(self, exec_ctx):
        return RTResult().success(str(exec_ctx.symbol_table.get('value')))
    execute_print_ret.arg_names = ['value']
    
    def execute_input(self, exec_ctx):
        text = input()
        return RTResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")
        return RTResult().success(Number(number))
    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        os.system('cls' if os.name == 'nt' else 'clear')
        return RTResult().success(Number.null)
    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get('value'), Number)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ['value']

    def execute_is_string(self, exec_ctx):
        is_string = isinstance(exec_ctx.symbol_table.get('value'), String)
        return RTResult().success(Number.true if is_string else Number.false)
    execute_is_string.arg_names = ['value']
    
    def execute_is_list(self, exec_ctx):
        is_list = isinstance(exec_ctx.symbol_table.get('value'), List)
        return RTResult().success(Number.true if is_list else Number.false)
    execute_is_list.arg_names = ['value']
    
    def execute_is_function(self, exec_ctx):
        is_function = isinstance(exec_ctx.symbol_table.get('value'), BaseFunction)
        return RTResult().success(Number.true if is_function else Number.false)
    execute_is_function.arg_names = ['value']

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))
        list_.elements.append(value)
        return RTResult().success(Number.null)
    execute_append.arg_names = ['list', 'value']

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index  = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))
        if not isinstance(index, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be number",
                exec_ctx
            ))
        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                'Element at this index could not be removed from list because index is out of bound',
                exec_ctx
            ))

        return RTResult().success(element)
    execute_pop.arg_names = ['list', 'index']

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))
        if not isinstance(listB, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be number",
                exec_ctx
            ))
        listA.elements.extend(listB.elements)
        return RTResult().success(Number.null)
        
    execute_extend.arg_names = ['listA', 'listB']

    def execute_len(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get('list')

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be list",
                exec_ctx
            ))
        return RTResult().success(Number(len(list_.elements)))
    execute_len.arg_names = ['list']

    def execute_run(self, exec_ctx):
        fn = exec_ctx.symbol_table.get('fn')

        if not isinstance(fn, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be String",
                exec_ctx
            ))
        
        fn = fn.value
        try:
            with open(fn, "r", encoding='utf-8') as f:
                script = f.read()
        except Exception as e:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Failed to load script \"{fn}\"\n" + str(e),
                exec_ctx
            ))
        _, error = run(fn, script)

        if error: 
            return RTResult().failure(RTError(
                self.pos_start,
                self.pos_end,
                f"Failed to finish executing script \"{fn}\"\n" +
                error.as_string(),
                exec_ctx
            ))
        
        return RTResult().success(Number.null)
    execute_run.arg_names = ['fn']


BuildInFunction.print                = BuildInFunction("print")
BuildInFunction.print_ret            = BuildInFunction("print_ret")
BuildInFunction.input                = BuildInFunction("input")
BuildInFunction.input_int            = BuildInFunction("input_int")
BuildInFunction.clear                = BuildInFunction("clear")
BuildInFunction.is_number            = BuildInFunction("is_number")
BuildInFunction.is_string            = BuildInFunction("is_string")
BuildInFunction.is_list              = BuildInFunction("is_list")
BuildInFunction.is_function          = BuildInFunction("is_function")
BuildInFunction.append               = BuildInFunction("append")
BuildInFunction.pop                  = BuildInFunction("pop")
BuildInFunction.extend               = BuildInFunction("extend")
BuildInFunction.run                  = BuildInFunction("run")
BuildInFunction.len                  = BuildInFunction("len")


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


'''
PRINT
PRINT_RET
INPUT
INPUT_INT
CLEAR
IS_NUMBER
IS_STRING
IS_LIST
IS_FUNCTION
APPEND
POP
EXTEND
'''
    

