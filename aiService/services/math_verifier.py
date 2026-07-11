"""
CB-16: Symbolic Math Verification Layer
Uses SymPy to independently verify Cal's mathematical answers.
"""

import re
import sympy as sp
from typing import Tuple, Optional, List

x, y, z, t, u, v = sp.symbols('x y z t u v', real=True)
COMMON_SYMBOLS = {'x': x, 'y': y, 'z': z, 't': t, 'u': u, 'v': v}


def extract_boxed_answer(cal_response: str) -> Optional[str]:
    """Extract the content inside \boxed{...}."""
    match = re.search(r'\\boxed\{([^}]*)\}', cal_response)
    if match:
        return match.group(1).strip()
    return None


def detect_variables_in_question(question: str) -> list:
    """Detect which variables are mentioned in the question."""
    variables = []
    for var in ['x', 'y', 'z', 't', 'u', 'v']:
        if re.search(rf'\b{var}\b', question):
            variables.append(var)
    return variables or ['x']


def parse_operation(question: str) -> Tuple[str, str, Optional[str]]:
    """Detect the math operation and extract the expression."""
    question_lower = question.lower()
    
    if 'partial' in question_lower and ('derivative' in question_lower or 'differentiate' in question_lower):
        var_match = re.search(r'(?:with respect to|w\.?r\.?t\.?)\s*([a-z])', question_lower)
        diff_var = var_match.group(1) if var_match else 'x'
        match = re.search(r'(?:partial\s+)?(?:derivative|differentiate)\s+(?:of\s+)?([^.?]+?)(?:\s+w\.?r\.?t\.|$)', question_lower)
        expr = match.group(1).strip() if match else 'x*y'
        return 'partial_derivative', expr, diff_var

    if 'derivative' in question_lower or 'differentiate' in question_lower:
        var_match = re.search(r'd/d([a-z])', question_lower)
        diff_var = var_match.group(1) if var_match else 'x'
        match = re.search(r'(?:derivative|differentiate)\s+(?:of\s+)?([^.?]+?)(?:\s+w\.?r\.?t\.|$)', question_lower)
        expr = match.group(1).strip() if match else 'x**2'
        return 'derivative', expr, diff_var

    if 'integral' in question_lower or 'integrate' in question_lower:
        match = re.search(r'(?:integral|integrate)\s+(?:of\s+)?([^.?]+)', question_lower)
        expr = match.group(1).strip() if match else 'x**2'
        return 'integral', expr, 'x'

    if 'limit' in question_lower:
        match = re.search(r'limit\s+(?:of\s+)?([^.?]+)', question_lower)
        expr = match.group(1).strip() if match else '1/x'
        return 'limit', expr, 'x'

    return 'simplify', question_lower.strip(), None


def sympy_solve(operation: str, expression_str: str, diff_var: Optional[str] = None) -> Optional[str]:
    """Use SymPy to solve the math problem."""
    try:
        expr = sp.sympify(expression_str, locals=COMMON_SYMBOLS)
        
        if operation == 'derivative' and diff_var:
            var = COMMON_SYMBOLS.get(diff_var, sp.Symbol(diff_var))
            result = sp.diff(expr, var)
        elif operation == 'partial_derivative' and diff_var:
            var = COMMON_SYMBOLS.get(diff_var, sp.Symbol(diff_var))
            result = sp.diff(expr, var)
        elif operation == 'integral':
            var = COMMON_SYMBOLS.get(diff_var, sp.Symbol(diff_var)) if diff_var else x
            result = sp.integrate(expr, var)
        elif operation == 'limit':
            var = COMMON_SYMBOLS.get(diff_var, sp.Symbol(diff_var)) if diff_var else x
            result = sp.limit(expr, var, sp.oo)
        else:
            result = sp.simplify(expr)
        
        return str(result)
    except Exception:
        return None


def verify_cal_math(question_text: str, cal_response: str) -> Tuple[Optional[bool], Optional[str], Optional[str]]:
    """Main verification function."""
    cal_answer = extract_boxed_answer(cal_response)
    if not cal_answer:
        return None, None, "No boxed answer found."

    try:
        operation, expr, diff_var = parse_operation(question_text)
    except Exception:
        return None, None, "Could not parse question."
    
    try:
        sympy_result = sympy_solve(operation, expr, diff_var)
    except Exception:
        sympy_result = None
    
    if sympy_result is None:
        return None, None, f"SymPy could not parse: {expr}"

    try:
        cal_expr = sp.sympify(cal_answer, locals=COMMON_SYMBOLS)
        sympy_expr = sp.sympify(sympy_result, locals=COMMON_SYMBOLS)
        is_correct = sp.simplify(cal_expr - sympy_expr) == 0
        return is_correct, sympy_result, None
    except Exception:
        return False, sympy_result, "Could not parse answer."
