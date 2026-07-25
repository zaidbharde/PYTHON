import ast
import operator as op
import re

# ---------------- SAFE EXPRESSION EVALUATOR ---------------- #

class SafeEval(ast.NodeVisitor):
    ALLOWED_BINOPS = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Mod: op.mod,
        ast.Pow: op.pow,
    }

    ALLOWED_UNARYOPS = {
        ast.UAdd: op.pos,
        ast.USub: op.neg,
        ast.Not: op.not_,
    }

    ALLOWED_CMPOPS = {
        ast.Eq: op.eq,
        ast.NotEq: op.ne,
        ast.Lt: op.lt,
        ast.LtE: op.le,
        ast.Gt: op.gt,
        ast.GtE: op.ge,
    }

    def __init__(self, variables):
        self.variables = variables

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        return node.value

    def visit_Name(self, node):
        if node.id in self.variables:
            return self.variables[node.id]
        raise NameError(f"Undefined variable: {node.id}")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type not in self.ALLOWED_BINOPS:
            raise ValueError("Operator not allowed")
        return self.ALLOWED_BINOPS[op_type](left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type not in self.ALLOWED_UNARYOPS:
            raise ValueError("Unary operator not allowed")
        return self.ALLOWED_UNARYOPS[op_type](operand)

    def visit_Compare(self, node):
        left = self.visit(node.left)
        for op_node, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            op_type = type(op_node)
            if op_type not in self.ALLOWED_CMPOPS:
                raise ValueError("Comparison operator not allowed")
            if not self.ALLOWED_CMPOPS[op_type](left, right):
                return False
            left = right
        return True

    def visit_BoolOp(self, node):
        if isinstance(node.op, ast.And):
            return all(self.visit(v) for v in node.values)
        elif isinstance(node.op, ast.Or):
            return any(self.visit(v) for v in node.values)
        raise ValueError("Bool operator not allowed")

    def generic_visit(self, node):
        raise ValueError(f"Invalid expression: {type(node).__name__}")


def safe_eval(expr, variables):
    tree = ast.parse(expr, mode="eval")
    return SafeEval(variables).visit(tree)


# ---------------- MINI LANGUAGE INTERPRETER ---------------- #

class MiniLang:
    def __init__(self, program_text):
        self.lines = [line.strip() for line in program_text.splitlines()]
        self.vars = {}
        self.labels = self._scan_labels()
        self.running = True

    def _scan_labels(self):
        labels = {}
        for i, line in enumerate(self.lines):
            if line.upper().startswith("LABEL "):
                label_name = line[6:].strip()
                labels[label_name] = i + 1  # jump to next line after label
        return labels

    def parse_value(self, expr):
        expr = expr.strip()
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        return safe_eval(expr, self.vars)

    def execute_line(self, line, pc):
        if not line or line.startswith("#"):
            return pc + 1

        upper = line.upper()

        # LABEL
        if upper.startswith("LABEL "):
            return pc + 1

        # PRINT
        if upper.startswith("PRINT "):
            expr = line[6:].strip()
            value = self.parse_value(expr)
            print(value)
            return pc + 1

        # LET variable = expression
        if upper.startswith("LET "):
            match = re.match(r"LET\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)", line, re.I)
            if not match:
                raise SyntaxError(f"Invalid LET syntax at line {pc+1}")
            var_name = match.group(1)
            expr = match.group(2)
            self.vars[var_name] = self.parse_value(expr)
            return pc + 1

        # INPUT variable "Prompt"
        if upper.startswith("INPUT "):
            match = re.match(r'INPUT\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s+(".*?"|\'.*?\'))?$', line, re.I)
            if not match:
                raise SyntaxError(f"Invalid INPUT syntax at line {pc+1}")
            var_name = match.group(1)
            prompt = match.group(2)
            prompt_text = prompt[1:-1] if prompt else f"{var_name}: "
            value = input(prompt_text)

            # auto convert number if possible
            if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
                value = int(value)
            else:
                try:
                    value = float(value)
                except:
                    pass

            self.vars[var_name] = value
            return pc + 1

        # IF condition THEN command
        if upper.startswith("IF "):
            if " THEN " not in upper:
                raise SyntaxError(f"Invalid IF syntax at line {pc+1}")
            parts = re.split(r"\bTHEN\b", line, maxsplit=1, flags=re.I)
            condition = parts[0][3:].strip()
            command = parts[1].strip()

            if safe_eval(condition, self.vars):
                return self.execute_line(command, pc)
            return pc + 1

        # GOTO label
        if upper.startswith("GOTO "):
            label_name = line[5:].strip()
            if label_name not in self.labels:
                raise ValueError(f"Label not found: {label_name}")
            return self.labels[label_name]

        # END
        if upper == "END":
            self.running = False
            return len(self.lines)

        raise SyntaxError(f"Unknown command at line {pc+1}: {line}")

    def run(self):
        pc = 0
        while pc < len(self.lines) and self.running:
            pc = self.execute_line(self.lines[pc], pc)


# ---------------- SAMPLE PROGRAM ---------------- #

program = """
# Custom mini language demo

PRINT "Welcome to MiniLang"
LET hp = 5
PRINT "Starting HP:"
PRINT hp

LABEL loop
PRINT "HP now:"
PRINT hp
LET hp = hp - 1
IF hp > 0 THEN GOTO loop

PRINT "Game Over"
END
"""

if __name__ == "__main__":
    interpreter = MiniLang(program)
    interpreter.run()
