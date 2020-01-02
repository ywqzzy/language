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
                "Expected '+', '-', '*' or '/' "
            ))
        return res

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        
        return self.current_tok
    
    def atom(self):
        res = ParseResult()
        tok = self.current_tok
        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
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

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-', or '(' "
        ))
    
    def power(self):
        return self.bin_op(self.atom, (TT_POW, ), self.factor)


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
                "EXPECTED '定义变量', 'VAR', int, float, identifier, '+', '-' or '('"
            ))

        return res.success(node)


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