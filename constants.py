import string

EN_DIGITS = '0123456789'
ZH_DIGITS = '零一二三四五六七八九'
DIGITS = EN_DIGITS + ZH_DIGITS

ZH_DIGITS_DICT = {
    '零': '0',
    '一': '1',
    '二': '2',
    '三': '3',
    '四': '4',
    '五': '5',
    '六': '6',
    '七': '7',
    '八': '8',
    '九': '9',
    '十': '10',
}

LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

TT_INT     =    'INT'
TT_FLOAT   =    'FLOAT'
TT_STRING  =    'STRING'
TT_PLUS    =    'PLUS'
TT_MINUS   =    'MINUS'
TT_MUL     =    'MUL'
TT_DIV     =    'DIV'
TT_POW     =    'POW'
TT_LPAREN  =    'LPAREN'
TT_RPAREN  =    'RPAREN'
TT_EE      =    'EE'
TT_NE      =    'NE'
TT_LT      =    'LT'
TT_GT      =    'GT'
TT_LTE     =    'LTE'
TT_GTE     =    'GTE'
TT_EOF     =    'EOF'
TT_COMMA   =    'COMMA'
TT_ARROW   =    'ARROW'


TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD    = 'KEYWORD'
TT_EQ         = 'EQ'

KEY_SYMBOL = '加减乘除'

KEYWORDS = [
    '定义变量',
    'VAR',
    'AND',
    'OR',
    'NOT',
    '如果',
    '那么',
    '不然',
    '否则',
    'IF',
    'THEN',
    'ELIF',
    'ELSE',
    'FOR',
    '从',
    'TO',
    '到',
    'STEP',
    '步长',
    'WHILE',
    '当',
    '开始',
    'FUN',
    '魔力法典',
]