from .state import WF003State
from tools.read_data import read_data
from tools.validate_data import validate_data

def read_vendor_file(state: WF003State) -> WF003State:
    source = state.get("vendor_file_source", "")
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    try:
        data = read_data(source)
        state["raw_records"] = data.get("records", [])
        steps.append("read_vendor_file: Success")
    except Exception as e:
        errors.append(f"read_vendor_file error: {str(e)}")
        steps.append("read_vendor_file: Failed")
        state["raw_records"] = []
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def validate_vendor_data(state: WF003State) -> WF003State:
    raw_records = state.get("raw_records", [])
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    if not raw_records and not errors:
        errors.append("validate_vendor_data error: No records to validate.")
        state["errors"] = errors
        steps.append("validate_vendor_data: Failed (Empty records)")
        state["execution_steps"] = steps
        return state
        
    if not raw_records:
        return state
    
    schema = {
        "required": ["sku", "product_name"],
        "fields": {
            "sku": {
                "non-empty": True
            },
            "product_name": {
                "non-empty": True
            }
        }
    }
    
    try:
        validation_result = validate_data(raw_records, schema)
        state["valid_rows"] = validation_result.valid_rows
        state["invalid_rows"] = validation_result.invalid_rows
        state["validation_summary"] = validation_result.summary
        state["invalid_row_report"] = validation_result.errors
        steps.append("validate_vendor_data: Success")
    except Exception as e:
        errors.append(f"validate_vendor_data error: {str(e)}")
        steps.append("validate_vendor_data: Failed")
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def generate_result(state: WF003State) -> WF003State:
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    result = {
        "status": "success" if not errors else "completed_with_errors",
        "cleaned_dataset": state.get("valid_rows", []),
        "validation_summary": state.get("validation_summary", {}),
        "invalid_row_report": state.get("invalid_row_report", []),
        "errors": errors
    }
    
    state["final_result"] = result
    steps.append("generate_result: Completed")
    state["execution_steps"] = steps
    return state
