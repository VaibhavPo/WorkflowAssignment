from typing import Any, Dict, List, Optional, Union
import math

def _to_float(val: Any, name: str) -> float:
    """Helper to convert and validate numeric inputs."""
    if val is None:
        raise ValueError(f"Missing value for '{name}'")
    try:
        fval = float(val)
        if math.isnan(fval) or math.isinf(fval):
            raise ValueError(f"Invalid numeric value for '{name}': {val}")
        return fval
    except (ValueError, TypeError):
        raise ValueError(f"Invalid numeric value for '{name}': {val}")

def _to_float_list(vals: Any, name: str) -> List[float]:
    """Helper to convert and validate list of numeric inputs."""
    if vals is None:
        raise ValueError(f"Missing value for '{name}'")
    if not isinstance(vals, (list, tuple)):
        raise ValueError(f"Expected a list or tuple for '{name}'")
    if not vals:
        raise ValueError(f"Empty list provided for '{name}'")
    return [_to_float(v, f"{name}[{i}]") for i, v in enumerate(vals)]

def calculate(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Perform business calculations required by different workflows.
    
    Operations supported:
    - 'percentage_difference': Requires 'current' and 'base' (or 'previous'). Returns %.
    - 'subtraction': Requires 'a' and 'b'. Returns a - b.
    - 'addition': Requires 'values' (a list) or 'a' and 'b'.
    - 'multiplication': Requires 'values' (a list) or 'a' and 'b'.
    - 'division': Requires 'numerator' and 'denominator'.
    - 'reorder_quantity': Requires 'minimum_stock' and 'current_stock'.
    - 'aggregation': Requires 'values' (a list). Returns sum.
    - 'success/failure rate' (or 'success_rate', 'failure_rate'): Requires 'total' and either 'successes' or 'failures'.
    - 'average': Requires 'values' (a list).
    - 'threshold_comparison': Requires 'value', 'threshold', and optional 'operator' (e.g., '>', '<', '>=', '<=', '==', '!='). Returns bool.
    
    Returns:
    Dict with keys 'status', 'result', and 'message'.
    
    Examples:
        >>> calculate("percentage_difference", current=110, base=100)
        {'status': 'success', 'result': 10.0, 'message': 'Calculation successful'}
        >>> calculate("division", numerator=10, denominator=0)
        {'status': 'error', 'result': None, 'message': 'Cannot divide by zero'}
    """
    try:
        if not isinstance(operation, str):
            raise ValueError("Operation must be a string")
            
        op = operation.lower().strip().replace("_", " ")
        
        if op == "percentage difference":
            current = _to_float(kwargs.get("current"), "current")
            base_val = kwargs.get("base") if "base" in kwargs else kwargs.get("previous")
            base = _to_float(base_val, "base/previous")
            if base == 0:
                raise ZeroDivisionError("Cannot calculate percentage difference with a base of 0")
            result = ((current - base) / abs(base)) * 100.0
            
        elif op == "subtraction":
            a = _to_float(kwargs.get("a"), "a")
            b = _to_float(kwargs.get("b"), "b")
            result = a - b
            
        elif op in ("addition", "aggregation"):
            if "values" in kwargs:
                vals = _to_float_list(kwargs.get("values"), "values")
                result = sum(vals)
            else:
                a = _to_float(kwargs.get("a"), "a")
                b = _to_float(kwargs.get("b"), "b")
                result = a + b
                
        elif op == "multiplication":
            if "values" in kwargs:
                vals = _to_float_list(kwargs.get("values"), "values")
                result = 1.0
                for v in vals:
                    result *= v
            else:
                a = _to_float(kwargs.get("a"), "a")
                b = _to_float(kwargs.get("b"), "b")
                result = a * b
                
        elif op == "division":
            numerator = _to_float(kwargs.get("numerator"), "numerator")
            denominator = _to_float(kwargs.get("denominator"), "denominator")
            if denominator == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            result = numerator / denominator
            
        elif op in ("reorder quantity", "reorder_quantity"):
            min_stock = _to_float(kwargs.get("minimum_stock"), "minimum_stock")
            curr_stock = _to_float(kwargs.get("current_stock"), "current_stock")
            result = max(0.0, min_stock - curr_stock)
            
        elif op in ("success/failure rate", "success rate", "failure rate"):
            total = _to_float(kwargs.get("total"), "total")
            if total == 0:
                raise ZeroDivisionError("Total cannot be zero")
            if "successes" in kwargs:
                count = _to_float(kwargs.get("successes"), "successes")
            elif "failures" in kwargs:
                count = _to_float(kwargs.get("failures"), "failures")
            else:
                raise ValueError("Must provide either 'successes' or 'failures'")
            result = count / total
            
        elif op == "average":
            vals = _to_float_list(kwargs.get("values"), "values")
            result = sum(vals) / len(vals)
            
        elif op == "threshold comparison":
            value = _to_float(kwargs.get("value"), "value")
            threshold = _to_float(kwargs.get("threshold"), "threshold")
            operator = kwargs.get("operator", ">")
            
            if operator == ">":
                result = value > threshold
            elif operator == "<":
                result = value < threshold
            elif operator == ">=":
                result = value >= threshold
            elif operator == "<=":
                result = value <= threshold
            elif operator == "==":
                result = value == threshold
            elif operator == "!=":
                result = value != threshold
            else:
                raise ValueError(f"Unsupported operator: {operator}")
                
        else:
            return {
                "status": "error",
                "result": None,
                "message": f"Unsupported operation: {operation}"
            }
            
        return {
            "status": "success",
            "result": result,
            "message": "Calculation successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "result": None,
            "message": str(e)
        }
