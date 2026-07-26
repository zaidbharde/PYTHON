from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

class TokenType(Enum):
    INT     = auto(); FLOAT   = auto(); STRING  = auto()
    IDENT   = auto(); BOOL    = auto()
    PLUS    = auto(); MINUS   = auto(); STAR    = auto()
    SLASH   = auto(); PERCENT = auto(); ASSIGN  = auto()
    EQ      = auto(); NEQ     = auto(); LT      = auto()
    GT      = auto(); LTE     = auto(); GTE     = auto()
    AND     = auto(); OR      = auto(); NOT     = auto()
    LPAREN  = auto(); RPAREN  = auto(); LBRACE  = auto()
    RBRACE  = auto(); COMMA   = auto(); SEMI    = auto()
    IF      = auto(); ELSE    = auto(); WHILE   = auto()
    FOR     = auto(); FN      = auto(); RETURN  = auto()
    LET     = auto(); PRINT   = auto(); EOF     = auto()

@dataclass
class Token:
    type:  TokenType
    value: Any
    line:  int

KEYWORDS = {
    "if": TokenType.IF, "else": TokenType.ELSE, "while": TokenType.WHILE,
    "for": TokenType.FOR, "fn": TokenType.FN, "return": TokenType.RETURN,
    "let": TokenType.LET, "print": TokenType.PRINT,
    "true": TokenType.BOOL, "false": TokenType.BOOL,
    "and": TokenType.AND, "or": TokenType.OR, "not": TokenType.NOT,
}

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1

    def peek(self): return self.source[self.pos] if self.pos < len(self.source) else '\0'
    def advance(self):
        ch = self.source[self.pos]; self.pos += 1
        if ch == '\n': self.line += 1
        return ch
    def match(self, expected):
        if self.pos < len(self.source) and self.source[self.pos] == expected:
            self.pos += 1; return True
        return False

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < len(self.source):
            ch = self.peek()
            if ch in ' \t\r\n': self.advance()
            elif ch == '#':
                while self.pos < len(self.source) and self.peek() != '\n': self.advance()
            elif ch.isdigit():  tokens.append(self.read_number())
            elif ch == '"':     tokens.append(self.read_string())
            elif ch.isalpha() or ch == '_': tokens.append(self.read_ident())
            elif ch == '+':  self.advance(); tokens.append(Token(TokenType.PLUS,   '+', self.line))
            elif ch == '-':  self.advance(); tokens.append(Token(TokenType.MINUS,  '-', self.line))
            elif ch == '*':  self.advance(); tokens.append(Token(TokenType.STAR,   '*', self.line))
            elif ch == '/':  self.advance(); tokens.append(Token(TokenType.SLASH,  '/', self.line))
            elif ch == '%':  self.advance(); tokens.append(Token(TokenType.PERCENT,'%', self.line))
            elif ch == '(':  self.advance(); tokens.append(Token(TokenType.LPAREN, '(', self.line))
            elif ch == ')':  self.advance(); tokens.append(Token(TokenType.RPAREN, ')', self.line))
            elif ch == '{':  self.advance(); tokens.append(Token(TokenType.LBRACE, '{', self.line))
            elif ch == '}':  self.advance(); tokens.append(Token(TokenType.RBRACE, '}', self.line))
            elif ch == ',':  self.advance(); tokens.append(Token(TokenType.COMMA,  ',', self.line))
            elif ch == ';':  self.advance(); tokens.append(Token(TokenType.SEMI,   ';', self.line))
            elif ch == '=':
                self.advance()
                if self.match('='): tokens.append(Token(TokenType.EQ, '==', self.line))
                else:               tokens.append(Token(TokenType.ASSIGN, '=', self.line))
            elif ch == '!':
                self.advance()
                if self.match('='): tokens.append(Token(TokenType.NEQ, '!=', self.line))
                else:               tokens.append(Token(TokenType.NOT, '!', self.line))
            elif ch == '<':
                self.advance()
                if self.match('='): tokens.append(Token(TokenType.LTE, '<=', self.line))
                else:               tokens.append(Token(TokenType.LT, '<', self.line))
            elif ch == '>':
                self.advance()
                if self.match('='): tokens.append(Token(TokenType.GTE, '>=', self.line))
                else:               tokens.append(Token(TokenType.GT, '>', self.line))
            else:
                raise SyntaxError(f"Unexpected character '{ch}' at line {self.line}")
        tokens.append(Token(TokenType.EOF, None, self.line))
        return tokens

    def read_number(self) -> Token:
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos].isdigit(): self.pos += 1
        if self.pos < len(self.source) and self.source[self.pos] == '.':
            self.pos += 1
            while self.pos < len(self.source) and self.source[self.pos].isdigit(): self.pos += 1
            return Token(TokenType.FLOAT, float(self.source[start:self.pos]), self.line)
        return Token(TokenType.INT, int(self.source[start:self.pos]), self.line)

    def read_string(self) -> Token:
        self.advance()
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos] != '"':
            if self.source[self.pos] == '\\': self.pos += 1
            self.pos += 1
        val = self.source[start:self.pos]
        self.advance()
        return Token(TokenType.STRING, val, self.line)

    def read_ident(self) -> Token:
        start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self.pos += 1
        word = self.source[start:self.pos]
        if word in KEYWORDS:
            tt = KEYWORDS[word]
            val = True if word == "true" else False if word == "false" else word
            return Token(tt, val, self.line)
        return Token(TokenType.IDENT, word, self.line)


class Node: pass

@dataclass
class NumLiteral(Node):     value: float
@dataclass
class StrLiteral(Node):     value: str
@dataclass
class BoolLiteral(Node):    value: bool
@dataclass
class Identifier(Node):     name: str
@dataclass
class BinOp(Node):          left: Node; op: str; right: Node
@dataclass
class UnaryOp(Node):        op: str; operand: Node
@dataclass
class Assignment(Node):     name: str; value: Node
@dataclass
class LetDecl(Node):        name: str; value: Node
@dataclass
class Block(Node):          statements: List[Node]
@dataclass
class IfStmt(Node):         condition: Node; then_block: Node; else_block: Optional[Node]
@dataclass
class WhileStmt(Node):      condition: Node; body: Node
@dataclass
class ForStmt(Node):        init: Node; condition: Node; update: Node; body: Node
@dataclass
class FnDecl(Node):         name: str; params: List[str]; body: Node
@dataclass
class FnCall(Node):         name: str; args: List[Node]
@dataclass
class ReturnStmt(Node):     value: Optional[Node]
@dataclass
class PrintStmt(Node):      value: Node

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos    = 0

    def current(self)   -> Token:     return self.tokens[self.pos]
    def advance(self)   -> Token:     t = self.tokens[self.pos]; self.pos += 1; return t
    def expect(self, tt: TokenType) -> Token:
        if self.current().type != tt:
            raise SyntaxError(f"Expected {tt.name}, got {self.current().type.name} at line {self.current().line}")
        return self.advance()

    def parse(self) -> List[Node]:
        stmts = []
        while self.current().type != TokenType.EOF:
            stmts.append(self.statement())
        return stmts

    def statement(self) -> Node:
        t = self.current().type
        if t == TokenType.LET:    return self.let_decl()
        if t == TokenType.IF:     return self.if_stmt()
        if t == TokenType.WHILE:  return self.while_stmt()
        if t == TokenType.FOR:    return self.for_stmt()
        if t == TokenType.FN:     return self.fn_decl()
        if t == TokenType.RETURN: return self.return_stmt()
        if t == TokenType.PRINT:  return self.print_stmt()
        if t == TokenType.LBRACE: return self.block()
        return self.expr_statement()

    def let_decl(self) -> LetDecl:
        self.advance()
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.ASSIGN)
        value = self.expression()
        self.expect(TokenType.SEMI)
        return LetDecl(name, value)

    def if_stmt(self) -> IfStmt:
        self.advance()
        self.expect(TokenType.LPAREN)
        cond = self.expression()
        self.expect(TokenType.RPAREN)
        then = self.block()
        else_block = None
        if self.current().type == TokenType.ELSE:
            self.advance()
            else_block = self.block() if self.current().type == TokenType.LBRACE else self.if_stmt()
        return IfStmt(cond, then, else_block)

    def while_stmt(self) -> WhileStmt:
        self.advance()
        self.expect(TokenType.LPAREN)
        cond = self.expression()
        self.expect(TokenType.RPAREN)
        body = self.block()
        return WhileStmt(cond, body)

    def for_stmt(self) -> ForStmt:
        self.advance()
        self.expect(TokenType.LPAREN)
        init = self.let_decl() if self.current().type == TokenType.LET else self.expr_statement()
        cond = self.expression()
        self.expect(TokenType.SEMI)
        update = self.expression()
        self.expect(TokenType.RPAREN)
        body = self.block()
        return ForStmt(init, cond, update, body)

    def fn_decl(self) -> FnDecl:
        self.advance()
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.LPAREN)
        params = []
        while self.current().type != TokenType.RPAREN:
            params.append(self.expect(TokenType.IDENT).value)
            if self.current().type == TokenType.COMMA: self.advance()
        self.expect(TokenType.RPAREN)
        body = self.block()
        return FnDecl(name, params, body)

    def return_stmt(self) -> ReturnStmt:
        self.advance()
        value = None
        if self.current().type != TokenType.SEMI:
            value = self.expression()
        self.expect(TokenType.SEMI)
        return ReturnStmt(value)

    def print_stmt(self) -> PrintStmt:
        self.advance()
        self.expect(TokenType.LPAREN)
        value = self.expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMI)
        return PrintStmt(value)

    def block(self) -> Block:
        self.expect(TokenType.LBRACE)
        stmts = []
        while self.current().type != TokenType.RBRACE:
            stmts.append(self.statement())
        self.expect(TokenType.RBRACE)
        return Block(stmts)

    def expr_statement(self) -> Node:
        expr = self.expression()
        self.expect(TokenType.SEMI)
        return expr

    def expression(self) -> Node: return self.assignment()

    def assignment(self) -> Node:
        expr = self.or_expr()
        if self.current().type == TokenType.ASSIGN:
            self.advance()
            if isinstance(expr, Identifier):
                return Assignment(expr.name, self.assignment())
            raise SyntaxError("Invalid assignment target")
        return expr

    def or_expr(self) -> Node:
        left = self.and_expr()
        while self.current().type == TokenType.OR:
            self.advance(); left = BinOp(left, "or", self.and_expr())
        return left

    def and_expr(self) -> Node:
        left = self.equality()
        while self.current().type == TokenType.AND:
            self.advance(); left = BinOp(left, "and", self.equality())
        return left

    def equality(self) -> Node:
        left = self.comparison()
        while self.current().type in (TokenType.EQ, TokenType.NEQ):
            op = self.advance().value; left = BinOp(left, op, self.comparison())
        return left

    def comparison(self) -> Node:
        left = self.addition()
        while self.current().type in (TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self.advance().value; left = BinOp(left, op, self.addition())
        return left

    def addition(self) -> Node:
        left = self.multiplication()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value; left = BinOp(left, op, self.multiplication())
        return left

    def multiplication(self) -> Node:
        left = self.unary()
        while self.current().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.advance().value; left = BinOp(left, op, self.unary())
        return left

    def unary(self) -> Node:
        if self.current().type in (TokenType.MINUS, TokenType.NOT):
            op = self.advance().value; return UnaryOp(op, self.unary())
        return self.primary()

    def primary(self) -> Node:
        t = self.current()
        if t.type == TokenType.INT:    self.advance(); return NumLiteral(float(t.value))
        if t.type == TokenType.FLOAT:  self.advance(); return NumLiteral(t.value)
        if t.type == TokenType.STRING: self.advance(); return StrLiteral(t.value)
        if t.type == TokenType.BOOL:   self.advance(); return BoolLiteral(t.value)
        if t.type == TokenType.IDENT:
            self.advance()
            if self.current().type == TokenType.LPAREN:
                self.advance()
                args = []
                while self.current().type != TokenType.RPAREN:
                    args.append(self.expression())
                    if self.current().type == TokenType.COMMA: self.advance()
                self.expect(TokenType.RPAREN)
                return FnCall(t.value, args)
            return Identifier(t.value)
        if t.type == TokenType.LPAREN:
            self.advance()
            expr = self.expression()
            self.expect(TokenType.RPAREN)
            return expr
        raise SyntaxError(f"Unexpected token: {t.type.name} at line {t.line}")


class ReturnException(Exception):
    def __init__(self, value): self.value = value

class Environment:
    def __init__(self, parent=None):
        self.vars   = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:   return self.vars[name]
        if self.parent:         return self.parent.get(name)
        raise NameError(f"Undefined variable: {name}")

    def set(self, name, value):
        if name in self.vars or not self.parent:
            self.vars[name] = value
        elif self.parent:
            try: self.parent.set(name, value)
            except: self.vars[name] = value

    def define(self, name, value):
        self.vars[name] = value


class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.output  = []

        self.globals.define("abs",   lambda args: abs(args[0]))
        self.globals.define("max",   lambda args: max(args))
        self.globals.define("min",   lambda args: min(args))
        self.globals.define("len",   lambda args: len(args[0]) if isinstance(args[0], str) else 0)
        self.globals.define("str",   lambda args: str(args[0]))
        self.globals.define("int",   lambda args: int(args[0]))
        self.globals.define("float", lambda args: float(args[0]))

    def run(self, source: str) -> List[str]:
        self.output = []
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
        for node in ast:
            self.execute(node, self.globals)
        return self.output

    def execute(self, node: Node, env: Environment) -> Any:
        if isinstance(node, NumLiteral):   return node.value
        if isinstance(node, StrLiteral):   return node.value
        if isinstance(node, BoolLiteral):  return node.value
        if isinstance(node, Identifier):   return env.get(node.name)

        if isinstance(node, BinOp):
            left  = self.execute(node.left, env)
            if node.op == "and": return left and self.execute(node.right, env)
            if node.op == "or":  return left or  self.execute(node.right, env)
            right = self.execute(node.right, env)
            ops = {'+': lambda a,b: a+b, '-': lambda a,b: a-b,
                   '*': lambda a,b: a*b, '/': lambda a,b: a/b,
                   '%': lambda a,b: a%b, '==': lambda a,b: a==b,
                   '!=': lambda a,b: a!=b, '<': lambda a,b: a<b,
                   '>': lambda a,b: a>b, '<=': lambda a,b: a<=b,
                   '>=': lambda a,b: a>=b}
            return ops[node.op](left, right)

        if isinstance(node, UnaryOp):
            val = self.execute(node.operand, env)
            if node.op == '-': return -val
            if node.op in ('!', 'not'): return not val

        if isinstance(node, LetDecl):
            val = self.execute(node.value, env)
            env.define(node.name, val)
            return val

        if isinstance(node, Assignment):
            val = self.execute(node.value, env)
            env.set(node.name, val)
            return val

        if isinstance(node, Block):
            result = None
            block_env = Environment(env)
            for stmt in node.statements:
                result = self.execute(stmt, block_env)
            return result

        if isinstance(node, IfStmt):
            if self.execute(node.condition, env):
                return self.execute(node.then_block, env)
            elif node.else_block:
                return self.execute(node.else_block, env)

        if isinstance(node, WhileStmt):
            while self.execute(node.condition, env):
                self.execute(node.body, env)

        if isinstance(node, ForStmt):
            for_env = Environment(env)
            self.execute(node.init, for_env)
            while self.execute(node.condition, for_env):
                self.execute(node.body, for_env)
                self.execute(node.update, for_env)

        if isinstance(node, FnDecl):
            env.define(node.name, node)

        if isinstance(node, FnCall):
            fn = env.get(node.name)
            args = [self.execute(a, env) for a in node.args]
            if callable(fn):
                return fn(args)
            if isinstance(fn, FnDecl):
                fn_env = Environment(self.globals)
                for p, a in zip(fn.params, args):
                    fn_env.define(p, a)
                try:
                    self.execute(fn.body, fn_env)
                except ReturnException as ret:
                    return ret.value
                return None

        if isinstance(node, ReturnStmt):
            val = self.execute(node.value, env) if node.value else None
            raise ReturnException(val)

        if isinstance(node, PrintStmt):
            val = self.execute(node.value, env)
            display = str(val)
            if isinstance(val, float) and val == int(val):
                display = str(int(val))
            if isinstance(val, bool):
                display = "true" if val else "false"
            self.output.append(display)
            print(f"  >>> {display}")

        return None


if __name__ == "__main__":
    source = """
    # Variables and arithmetic
    let x = 10;
    let y = 20;
    let z = x * y + 5;
    print(z);

    # Strings
    let name = "World";
    let greeting = "Hello, " + name + "!";
    print(greeting);

    # Conditionals
    if (x > 5) {
        print("x is big");
    } else {
        print("x is small");
    }

    # Functions
    fn factorial(n) {
        if (n <= 1) { return 1; }
        return n * factorial(n - 1);
    }
    print(factorial(10));

    fn fibonacci(n) {
        if (n <= 1) { return n; }
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    print(fibonacci(15));

    # Loops
    let sum = 0;
    let i = 1;
    while (i <= 100) {
        sum = sum + i;
        i = i + 1;
    }
    print(sum);

    # For loop
    let product = 1;
    for (let j = 1; j <= 10; j = j + 1) {
        product = product * j;
    }
    print(product);

    # Higher-order patterns
    fn apply_twice(f, x) {
        return f(f(x));
    }
    fn double(n) { return n * 2; }
    print(apply_twice(double, 3));

    # Boolean logic
    let a = true;
    let b = false;
    print(a and b);
    print(a or b);
    print(not b);

    # Nested functions
    fn make_adder(n) {
        fn adder(x) { return x + n; }
        return adder;
    }
    """

    print("=" * 50)
    print("  Programming Language Interpreter")
    print("=" * 50)
    print()

    interpreter = Interpreter()
    output = interpreter.run(source)

    print(f"\n  Total output lines: {len(output)}")
