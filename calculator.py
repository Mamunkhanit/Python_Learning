import ast
import math
import operator
import re
import tkinter as tk


BACKGROUND = "#17231F"
DISPLAY_BACKGROUND = "#F2F0E8"
NUMBER_BACKGROUND = "#2B3C36"
NUMBER_HOVER = "#3B5048"
OPERATOR_BACKGROUND = "#E98A68"
EQUALS_BACKGROUND = "#B8D8C6"
TEXT_LIGHT = "#F4F2EA"
TEXT_DARK = "#17231F"
MUTED_TEXT = "#82948B"

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def evaluate(expression):
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](visit(node.left), visit(node.right))
        raise ValueError("Unsupported expression")

    result = visit(tree)
    if isinstance(result, float) and not math.isfinite(result):
        raise ValueError("Result is not finite")
    return result


def format_result(value):
    if isinstance(value, int):
        return str(value)
    return f"{value:.12g}"


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mamun's Calculator")
        self.configure(bg=BACKGROUND)
        self.geometry("380x560")
        self.minsize(320, 460)

        self.expression = ""
        self.history = ""
        self.just_evaluated = False
        self.has_error = False

        self._build_interface()
        self._bind_keyboard()
        self._refresh_display()

    def _build_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self, bg=BACKGROUND, padx=18, pady=14)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(
            header,
            text="Mamun's Calculator",
            bg=BACKGROUND,
            fg=TEXT_LIGHT,
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        tk.Label(
            header,
            text="PYTHON DESKTOP",
            bg=BACKGROUND,
            fg=MUTED_TEXT,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="right")

        display = tk.Frame(self, bg=DISPLAY_BACKGROUND, padx=18, pady=16)
        display.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 14))
        display.grid_columnconfigure(0, weight=1)
        display.grid_rowconfigure(1, weight=1)

        self.history_label = tk.Label(
            display,
            text="",
            anchor="e",
            bg=DISPLAY_BACKGROUND,
            fg="#718078",
            font=("Segoe UI", 11),
        )
        self.history_label.grid(row=0, column=0, sticky="ew")
        self.value_label = tk.Label(
            display,
            text="0",
            anchor="e",
            bg=DISPLAY_BACKGROUND,
            fg=TEXT_DARK,
            font=("Segoe UI", 42, "bold"),
        )
        self.value_label.grid(row=1, column=0, sticky="sew")

        keypad = tk.Frame(self, bg=BACKGROUND, padx=18)
        keypad.grid(row=2, column=0, sticky="nsew", pady=(0, 18))
        for column in range(4):
            keypad.grid_columnconfigure(column, weight=1, uniform="key", minsize=58)
        for row in range(5):
            keypad.grid_rowconfigure(row, weight=1, uniform="key", minsize=54)

        keys = [
            [("AC", "clear"), ("+/-", "sign"), ("DEL", "delete"), ("/", "divide")],
            [("7", "digit"), ("8", "digit"), ("9", "digit"), ("*", "multiply")],
            [("4", "digit"), ("5", "digit"), ("6", "digit"), ("-", "subtract")],
            [("1", "digit"), ("2", "digit"), ("3", "digit"), ("+", "add")],
            [("0", "digit"), (".", "decimal"), ("=", "equals")],
        ]

        for row, key_row in enumerate(keys):
            column = 0
            for label, action in key_row:
                span = 2 if row == 4 and label == "0" else 1
                self._create_button(keypad, label, action, row, column, span)
                column += span

    def _create_button(self, parent, label, action, row, column, span):
        if action in {"add", "subtract", "multiply", "divide"}:
            background, foreground, hover = OPERATOR_BACKGROUND, TEXT_DARK, "#F3A084"
        elif action == "equals":
            background, foreground, hover = EQUALS_BACKGROUND, TEXT_DARK, "#CBE5D6"
        elif action == "clear":
            background, foreground, hover = "#6C5148", TEXT_LIGHT, "#805F53"
        else:
            background, foreground, hover = NUMBER_BACKGROUND, TEXT_LIGHT, NUMBER_HOVER

        button = tk.Button(
            parent,
            text=label,
            command=lambda: self._activate(action, label),
            bg=background,
            fg=foreground,
            activebackground=hover,
            activeforeground=foreground,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 17 if len(label) < 3 else 12, "bold"),
            cursor="hand2",
        )
        button.grid(row=row, column=column, columnspan=span, sticky="nsew", padx=4, pady=4)

    def _bind_keyboard(self):
        self.bind_all("<Key>", self._on_key)

    def _on_key(self, event):
        if event.keysym in {"Return", "KP_Enter", "equal"}:
            self._activate("equals", "=")
        elif event.keysym == "BackSpace":
            self._activate("delete", "DEL")
        elif event.keysym == "Escape":
            self._activate("clear", "AC")
        elif event.char in "0123456789":
            self._activate("digit", event.char)
        elif event.char == ".":
            self._activate("decimal", ".")
        elif event.char in "+-*/":
            action = {"+": "add", "-": "subtract", "*": "multiply", "/": "divide"}[event.char]
            self._activate(action, event.char)

    def _activate(self, action, label):
        if action == "clear":
            self.expression = ""
            self.history = ""
            self.just_evaluated = False
            self.has_error = False
        elif action == "delete":
            if self.has_error or self.just_evaluated:
                self.expression = ""
            else:
                self.expression = self.expression[:-1]
            self.history = ""
            self.just_evaluated = False
            self.has_error = False
        elif action == "sign":
            self._toggle_sign()
        elif action == "digit":
            self._append_digit(label)
        elif action == "decimal":
            self._append_decimal()
        elif action in {"add", "subtract", "multiply", "divide"}:
            self._append_operator(label)
        elif action == "equals":
            self._calculate()
        self._refresh_display()

    def _prepare_input(self):
        if self.has_error or self.just_evaluated:
            self.expression = ""
        self.history = ""
        self.just_evaluated = False
        self.has_error = False

    def _append_digit(self, digit):
        self._prepare_input()
        if self.expression.endswith("0") and (
            len(self.expression) == 1 or self.expression[-2] in "+-*/"
        ):
            self.expression = self.expression[:-1] + digit
        else:
            self.expression += digit

    def _append_decimal(self):
        self._prepare_input()
        current_number = re.search(r"\d*\.?\d*$", self.expression).group()
        if "." in current_number:
            return
        if not current_number:
            self.expression += "0"
        self.expression += "."

    def _append_operator(self, symbol):
        if self.has_error:
            self.expression = ""
            self.has_error = False
        if self.just_evaluated:
            self.just_evaluated = False
        self.history = ""

        if not self.expression:
            if symbol == "-":
                self.expression = "-"
            return
        if self.expression.endswith("."):
            self.expression += "0"

        if self.expression[-1] in "+-*/":
            trailing_unary_minus = self.expression.endswith("-") and (
                len(self.expression) == 1 or self.expression[-2] in "+-*/"
            )
            if trailing_unary_minus:
                if symbol != "-" and len(self.expression) > 1:
                    self.expression = self.expression[:-2] + symbol
            elif symbol == "-" and self.expression[-1] in "+*/":
                self.expression += symbol
            else:
                self.expression = self.expression[:-1] + symbol
        else:
            self.expression += symbol

    def _toggle_sign(self):
        self._prepare_input()
        number = re.search(r"\d*\.?\d+$", self.expression)
        if number is None:
            if not self.expression:
                self.expression = "-"
            return

        start = number.start()
        if start > 0 and self.expression[start - 1] == "-" and (
            start == 1 or self.expression[start - 2] in "+-*/"
        ):
            self.expression = self.expression[: start - 1] + self.expression[start :]
        else:
            self.expression = self.expression[:start] + "-" + self.expression[start:]

    def _calculate(self):
        if not self.expression or self.expression.endswith(("+", "-", "*", "/")):
            return
        if self.expression.endswith("."):
            self.expression += "0"
        original = self.expression
        try:
            result = format_result(evaluate(original))
        except (ArithmeticError, SyntaxError, ValueError):
            self.expression = ""
            self.history = f"{original} ="
            self.has_error = True
            self.just_evaluated = True
            return

        self.expression = result
        self.history = f"{original} ="
        self.just_evaluated = True

    def _refresh_display(self):
        self.history_label.configure(text=self.history or self.expression or " ")
        if self.has_error:
            value = "Error"
        elif not self.expression:
            value = "0"
        else:
            try:
                value = format_result(evaluate(self.expression))
            except (ArithmeticError, SyntaxError, ValueError):
                trailing_number = re.search(r"\d*\.?\d+$", self.expression)
                value = trailing_number.group() if trailing_number else self.expression

        font_size = max(24, 42 - max(0, len(value) - 9) * 2)
        self.value_label.configure(text=value, font=("Segoe UI", font_size, "bold"))


if __name__ == "__main__":
    Calculator().mainloop()