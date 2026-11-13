from __future__ import annotations

import ast
import math
import operator


class MathSecurityError(ValueError):
    """Raised when an expression contains a non-whitelisted AST node."""


_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_ALLOWED_FUNCS = {
    "sqrt": math.sqrt,
    "ceil": math.ceil,
    "floor": math.floor,
    "abs": abs,
    "round": round,
}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left, right = _eval(node.left), _eval(node.right)
        value = _ALLOWED_BINOPS[type(node.op)](left, right)
        if abs(value) > 1e15:
            raise MathSecurityError("Result is outside the allowed numeric range")
        return float(value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return float(_ALLOWED_UNARY[type(node.op)](_eval(node.operand)))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCS:
        if node.keywords:
            raise MathSecurityError("Keyword arguments are not allowed")
        return float(_ALLOWED_FUNCS[node.func.id](*[_eval(a) for a in node.args]))
    raise MathSecurityError(f"Blocked expression node: {type(node).__name__}")


def calculate_expression(expression: str) -> str:
    """Safely evaluate arithmetic without eval() or exec()."""
    if len(expression) > 200:
        raise MathSecurityError("Expression is too long")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise MathSecurityError("Invalid mathematical expression") from exc
    value = _eval(tree)
    return f"{value:g}"
