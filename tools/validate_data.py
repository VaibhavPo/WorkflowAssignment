import math
from typing import List, Dict, Any, Optional

class ValidationResult:
    """
    Holds the result of a data validation operation.
    """
    def __init__(self, valid_rows: List[Dict[str, Any]], invalid_rows: List[Dict[str, Any]], errors: List[Dict[str, Any]], summary: Dict[str, int]):
        self.valid_rows = valid_rows
        self.invalid_rows = invalid_rows
        self.errors = errors
        self.summary = summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid_rows": self.valid_rows,
            "invalid_rows": self.invalid_rows,
            "errors": self.errors,
            "summary": self.summary
        }


def validate_data(data: List[Dict[str, Any]], schema: Dict[str, Any]) -> ValidationResult:
    """
    Validate structured business data against workflow-provided validation rules.
    
    The schema should be a dictionary defining rules. Example:
    {
        "required": ["SKU", "product_name"],
        "fields": {
            "SKU": {
                "type": "string",
                "non-empty": True
            },
            "quantity": {
                "type": "integer",
                "minimum": 0
            },
            "status": {
                "type": "string",
                "allowed_values": ["active", "inactive", "pending"]
            }
        }
    }
    
    Supported constraints:
    - required: list of required fields at the root or `{"required": True}` in field rules.
    - type: "string", "integer", "float", "boolean", "number"
    - non-empty: True (for strings)
    - minimum/maximum: numeric constraints
    - allowed_values: list of allowed values
    
    Args:
        data (List[Dict[str, Any]]): A list of dictionaries representing the data records.
        schema (Dict[str, Any]): The validation schema.

    Returns:
        ValidationResult: An object containing valid rows, invalid rows, specific errors per row, and a summary.
    """
    valid_rows = []
    invalid_rows = []
    errors = []
    
    fields_schema = schema.get("fields", {})
    global_required = schema.get("required_fields", [])
    if "required" in schema and isinstance(schema["required"], list):
        global_required.extend(schema["required"])
        
    for index, row in enumerate(data):
        row_errors = []
        
        # Check globally required fields
        for req_field in global_required:
            if req_field not in row or _is_null(row[req_field]):
                row_errors.append({"field": req_field, "error": f"Missing or null required field: '{req_field}'"})

        # Check field-specific rules
        for field, rules in fields_schema.items():
            value = row.get(field)
            
            # Check required via field rules
            is_required = rules.get("required", False)
            if is_required and (field not in row or _is_null(value)):
                 if field not in global_required:
                     row_errors.append({"field": field, "error": f"Missing or null required field: '{field}'"})
                 continue

            # Skip further validation for null/missing values if they are not required
            if field not in row or _is_null(value):
                continue

            # Check type
            expected_type = rules.get("type")
            if expected_type:
                if not _check_type(value, expected_type):
                    row_errors.append({"field": field, "error": f"Invalid type for '{field}'. Expected {expected_type}, got {type(value).__name__}."})
                    continue

            # Check non-empty (for strings)
            if rules.get("non-empty") and isinstance(value, str) and not value.strip():
                row_errors.append({"field": field, "error": f"Field '{field}' cannot be empty."})

            # Check minimum/maximum (for numbers)
            if "minimum" in rules and isinstance(value, (int, float)):
                if value < rules["minimum"]:
                    row_errors.append({"field": field, "error": f"Value {value} for '{field}' is less than minimum {rules['minimum']}."})
            if "maximum" in rules and isinstance(value, (int, float)):
                if value > rules["maximum"]:
                    row_errors.append({"field": field, "error": f"Value {value} for '{field}' is greater than maximum {rules['maximum']}."})

            # Check allowed values
            if "allowed_values" in rules:
                if value not in rules["allowed_values"]:
                    row_errors.append({"field": field, "error": f"Value {value} for '{field}' not in allowed values: {rules['allowed_values']}."})

        if row_errors:
            invalid_rows.append(row)
            errors.append({"row_index": index, "row_data": row, "errors": row_errors})
        else:
            valid_rows.append(row)

    summary = {
        "total_rows": len(data),
        "valid_count": len(valid_rows),
        "invalid_count": len(invalid_rows),
        "error_count": sum(len(e["errors"]) for e in errors)
    }
    
    return ValidationResult(valid_rows=valid_rows, invalid_rows=invalid_rows, errors=errors, summary=summary)

def _is_null(value: Any) -> bool:
    """Helper to determine if a value is conceptually 'null' or missing."""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False

def _check_type(value: Any, expected_type: str) -> bool:
    """Helper to check if a value matches the expected type string."""
    if expected_type == "string":
        return isinstance(value, str)
    elif expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    elif expected_type == "float":
        return isinstance(value, float)
    elif expected_type == "boolean":
        return isinstance(value, bool)
    elif expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True  # Unknown type is ignored or could be implemented as an error

if __name__ == "__main__":
    # Example usage
    sample_data = [
        {"SKU": "A123", "quantity": 10, "status": "active"},
        {"SKU": "B456", "quantity": -5, "status": "pending"},
        {"quantity": 20, "status": "active"},
        {"SKU": "", "quantity": 5, "status": "active"}
    ]
    
    sample_schema = {
        "required": ["SKU"],
        "fields": {
            "SKU": {
                "type": "string",
                "non-empty": True
            },
            "quantity": {
                "type": "integer",
                "minimum": 0
            },
            "status": {
                "type": "string",
                "allowed_values": ["active", "inactive"]
            }
        }
    }
    
    result = validate_data(sample_data, sample_schema)
    import json
    print(json.dumps(result.to_dict(), indent=2))
