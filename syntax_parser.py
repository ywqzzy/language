from node import *
from tokens import *
from constants import *
from error import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()


    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'AND' or 'OR'"
			))
        return res

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        
        return self.current_tok

    def power(self):
        return self.bin_op(self.call, (TT_POW, ), self.factor)

    def call(self):
        res = ParseResult()

        atom = res.register(self.atom())

        if res.error: return res
        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error: 
                    return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(' or 'NOT'"
					))
                
                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ',' or ')"
                    ))
                
                res.register_advancement()
                self.advance()
            return res.success(CallNode(
                atom, arg_nodes
            ))
        return res.success(atom)
    
    def atom(self):
        res = ParseResult()
        tok = self.current_tok
        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
            
        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))
        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')' "
                ))
        elif tok.matches(TT_KEYWORD, 'IF') or tok.matches(TT_KEYWORD, '如果'):  #TODO
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)
        elif tok.matches(TT_KEYWORD, 'FOR') or tok.matches(TT_KEYWORD, '从'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)
        elif tok.matches(TT_KEYWORD, 'WHILE') or tok.matches(TT_KEYWORD, '当'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)
        elif tok.matches(TT_KEYWORD, 'FUN') or tok.matches(TT_KEYWORD, '魔力法典'):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-', or '(', 'IF', 'FOR', 'WHILE', 'FUN' "
        ))
    

    def factor(self):
        res = ParseResult()

        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))
       
        return self.power()


    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None
        if not (self.current_tok.matches(TT_KEYWORD, 'IF') or self.current_tok.matches(TT_KEYWORD, '如果')) :    #TODO
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'IF'，'如果'" #TODO
            ))
        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not (self.current_tok.matches(TT_KEYWORD, 'THEN') or self.current_tok.matches(TT_KEYWORD, '那么')): #TODO
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'THEN','那么'" #TODO
            ))
        
        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error: return res
        cases.append((condition, expr))

        while (self.current_tok.matches(TT_KEYWORD, 'ELIF') or self.current_tok.matches(TT_KEYWORD, '不然')): #TODO
            res.register_advancement()
            self.advance()
            
            condition = res.register(self.expr())
            if res.error: return res
            
            if not (self.current_tok.matches(TT_KEYWORD, 'THEN') or self.current_tok.matches(TT_KEYWORD, '那么')): #TODO
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'THEN', '那么'"  #TODO
                ))
            
            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error: return res

            cases.append((condition, expr))

        if self.current_tok.matches(TT_KEYWORD, 'ELSE') or self.current_tok.matches(TT_KEYWORD, '否则'): #TODO
            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error: return res
            else_case = expr

        return res.success(IfNode(cases, else_case))
    
    def for_expr(self):
        res = ParseResult()

        if not (self.current_tok.matches(TT_KEYWORD, 'FOR') or self.current_tok.matches(TT_KEYWORD, '从')): #TODO
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'FOR' or '从'"
            ))
        
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_start,
                f"Expected identifier"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '='"
            ))
        
        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error: return res
        # print("type")
        # print(self.current_tok.type)
        # print("value")
        # print(self.current_tok.value)

        if self.current_tok.matches(TT_KEYWORD, 'TO') == False and self.current_tok.matches(TT_KEYWORD, '到') == False: #TODO
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'TO' or '到'"
            ))
        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error: return res

        if self.current_tok.matches(TT_KEYWORD, 'STEP') or self.current_tok.matches(TT_KEYWORD, '步长'): #TODO
            res.register_advancement()
            self.advance()

            step_value =   res.register(self.expr())
            if res.error: return res
        else:
            step_value = None
        
        if not (self.current_tok.matches(TT_KEYWORD, 'THEN') or self.current_tok.matches(TT_KEYWORD, '开始')): #TODO
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'THEN' or '开始'"
            ))
        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error: return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))

    def while_expr(self): 
        res = ParseResult()
        if not (self.current_tok.matches(TT_KEYWORD, 'WHILE') or self.current_tok.matches(TT_KEYWORD, '当')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'WHILE' or '当'"
            ))
        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        
        if res.error: return res

        if not (self.current_tok.matches(TT_KEYWORD, 'THEN') or self.current_tok.matches(TT_KEYWORD, '开始')): #TODO
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'THEN' or '开始'"
            ))
        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error: return res

        return res.success(WhileNode(condition, body))


    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    
    def comp_expr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'NOT'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())

            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))
        
        node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_LTE, TT_LT, TT_GT, TT_GTE, TT_NE)))
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected int, float, identifier, '+', '-', or '(', 'NOT' "
            ))
        return res.success(node)
    

    def expr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, '定义变量') or self.current_tok.matches(TT_KEYWORD, 'VAR'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier"
                ))
            var_name = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))
            
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, "AND"), (TT_KEYWORD, "OR"))))

        if res.error: 
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "EXPECTED '定义变量', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-' or '('"
            ))

        return res.success(node)
    
    def func_def(self):
        res = ParseResult()

        if not (self.current_tok.matches(TT_KEYWORD, 'FUN') or self.current_tok.matches(TT_KEYWORD, '魔力法典')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'FUN' or '魔力法典'"
            ))
        
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '('"
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expeced identifier or '(' "
                ))
        
        res.register_advancement()
        self.advance()

        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected identifier"
                    ))

            
                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier or ')"
                ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_ARROW:  # TODO  ARROW CAN BE 发动
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '->'"
            ))     
        
        res.register_advancement()
        self.advance()

        node_to_return = res.register(self.expr())
        if res.error: return res

        return res.success(FuncDefNode(
            var_name_tok,
            arg_name_toks,
            node_to_return
        ))



    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a
        
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        
        return res.success(left)



class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
    
    def register(self, res):   
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node
    
    def register_advancement(self):
        self.advance_count += 1
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self