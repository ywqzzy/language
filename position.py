class Position:
    def __init__(self, idx, line_num, col_num, file_name, file_text):
        self.file_name = file_name
        self.file_text = file_text
        self.idx = idx
        self.line_num = line_num
        self.col_num = col_num
    
    def advance(self, current_char=None):
        self.idx += 1 
        self.col_num += 1
        if current_char == '\n':
            self.line_num += 1
            self.col_num = 0
        return self

    def copy(self):
        return Position(self.idx, self.line_num, self.col_num, self.file_name, self.file_text)
        
