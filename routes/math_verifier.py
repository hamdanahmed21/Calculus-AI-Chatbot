"""
CB-16: Symbolic Math Verification Layer
Uses SymPy to independently verify Cal's mathematical answers.
Author: Hamza Ali
"""

import re
import sympy as sp
from typing import Tuple, Optional

# Initialize the main variable (we assume 'x' for now, can expand later)
x = sp.Symbol('x')
y = sp.Symbol('y')  # For multi-variable support


def extract_boxed_answer(cal_response: str) -> Optional[str]:
    """
    Extract the content inside \boxed{...} from Cal's response.
    Example: "The answer is \boxed{2x}" -> returns "2x"
    """
    # Regex to find \boxed{...} (handles nested braces roughly)
    match = re.search(r'\\boxed\{([^}]*)\}', cal_response)
    if match:
        return match.group(1).strip()
    return None


def parse_operation(question: str) -> Tuple[str, str]:
    """
    Detect the math operation required and extract the expression.
    Returns: (operation_type, expression_string)
    operation_type: 'derivative', 'integral', 'limit', 'simplify'
    """
    question_lower = question.lower()
    
    # Detect derivative
    if 'derivative' in question_lower or 'differentiate' in question_lower or "d/dx" in question_lower:
        # Try to find the function to derive
        # Example: "derivative of x**3" -> extract "x**3"
        match = re.search(r'(?:derivative|differentiate|d/dx)\s+(?:of\s+)?([\w\*\^\(\)\+\-\/]+)', question_lower)
        if match:
            return 'derivative', match.group(1)
        else:
            # If we can't parse, fallback to the whole math string
            return 'derivative', 'x**2'  # safe fallback

    # Detect integral
    if 'integral' in question_lower or 'integrate' in question_lower:
        match = re.search(r'(?:integral|integrate)\s+(?:of\s+)?([\w\*\^\(\)\+\-\/]+)', question_lower)
        if match:
            return 'integral', match.group(1)
        else:
            return 'integral', 'x**2'

    # Detect limit
    if 'limit' in question_lower:
        match = re.search(r'limit\s+(?:of\s+)?([\w\*\^\(\)\+\-\/]+)', question_lower)
        if match:
            return 'limit', match.group(1)
        else:
            return 'limit', '1/x'

    # Default: try to simplify or just evaluate
    return 'simplify', question_lower.strip()


def sympy_solve(operation: str, expression_str: str) -> Optional[str]:
    """
    Use SymPy to solve the math problem.
    """
    try:
        # Convert string to SymPy expression safely
        expr = sp.sympify(expression_str)
        
        if operation == 'derivative':
            result = sp.diff(expr, x)
        elif operation == 'integral':
            result = sp.integrate(expr, x)
        elif operation == 'limit':
            # Default limit to infinity, or we can parse more
            result = sp.limit(expr, x, sp.oo)
        else:  # simplify
            result = sp.simplify(expr)
        
        # Convert result to string, ensuring it's in a nice format
        return str(result)
    except (sp.SympifyError, TypeError, AttributeError) as e:
        print(f"SymPy Error: {e}")
        return None


def verify_cal_math(question_text: str, cal_response: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    The main verification function.
    Returns: (is_correct, sympy_answer, error_message)
    """
    # Step 1: Extract Cal's final answer
    cal_answer = extract_boxed_answer(cal_response)
    if not cal_answer:
        return False, None, "No boxed answer found in Cal's response."

    # Step 2: Parse the question to understand the operation
    operation, expr = parse_operation(question_text)
    
    # Step 3: Solve using SymPy
    sympy_result = sympy_solve(operation, expr)
    if sympy_result is None:
        # Fallback: We couldn't solve it (unsupported operation)
        return False, None, f"SymPy could not parse: {expr}"

    # Step 4: Compare SymPy's result with Cal's boxed answer
    # We need to simplify BOTH to ensure equality (e.g., 2*x vs 2x)
    try:
        cal_expr = sp.sympify(cal_answer)
        sympy_expr = sp.sympify(sympy_result)
        
        # Check if they are mathematically equivalent
        is_correct = sp.simplify(cal_expr - sympy_expr) == 0
        return is_correct, sympy_result, None
    except (sp.SympifyError, TypeError):
        # If Cal's answer can't be parsed, it's wrong
        return False, sympy_result, "Could not parse Cal's answer as math."
    
    
    
