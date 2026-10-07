from .state import WF001State
from tools.read_data import read_data
from tools.calculate import calculate
from .models import InventoryItem, RestockItem

def load_inventory(state: WF001State) -> WF001State:
    source = state.get("inventory_source", "")
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    try:
        data = read_data(source)
        state["inventory_records"] = data.get("records", [])
        steps.append("load_inventory: Success")
    except Exception as e:
        errors.append(f"load_inventory error: {str(e)}")
        steps.append("load_inventory: Failed")
        state["inventory_records"] = []
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def validate_inventory(state: WF001State) -> WF001State:
    raw_records = state.get("inventory_records", [])
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    valid_records = []
    for i, rec in enumerate(raw_records):
        if not isinstance(rec, dict):
            continue
            
        try:
            current_stock = float(rec.get("current_stock", 0))
            min_val = rec.get("minimum_stock")
            minimum_stock = float(min_val) if min_val is not None else None
            
            item = InventoryItem(
                product=rec.get("product_name") or rec.get("product", f"Unknown-{i}"),
                current_stock=current_stock,
                minimum_stock=minimum_stock
            )
            valid_records.append(item)
        except (ValueError, TypeError) as e:
            errors.append(f"Row {i+1} validation error: {str(e)} (Data: {rec})")
            
    state["valid_inventory_items"] = valid_records
    state["errors"] = errors
    steps.append(f"validate_inventory: Validated {len(valid_records)} records")
    state["execution_steps"] = steps
    return state

def evaluate_stock(state: WF001State) -> WF001State:
    records = state.get("valid_inventory_items", [])
    global_threshold = state.get("minimum_stock_threshold") or 0.0
    steps = state.get("execution_steps", [])
    
    low_stock_items = []
    for item in records:
        threshold = item.minimum_stock if item.minimum_stock is not None else global_threshold
        # Use generic calculate tool for threshold comparison
        calc_result = calculate(
            "threshold_comparison", 
            value=item.current_stock, 
            threshold=threshold, 
            operator="<"
        )
        if calc_result.get("status") == "success" and calc_result.get("result") is True:
            low_stock_items.append(item)
                
    state["low_stock_items"] = low_stock_items
    steps.append(f"evaluate_stock: Found {len(low_stock_items)} low stock items")
    state["execution_steps"] = steps
    return state

def calculate_reorder_quantities(state: WF001State) -> WF001State:
    low_stock_items = state.get("low_stock_items", [])
    global_threshold = state.get("minimum_stock_threshold") or 0.0
    steps = state.get("execution_steps", [])
    
    restock_items = []
    for item in low_stock_items:
        threshold = item.minimum_stock if item.minimum_stock is not None else global_threshold
        
        # Use generic calculate tool for reorder quantity
        calc_result = calculate(
            "reorder_quantity",
            minimum_stock=threshold,
            current_stock=item.current_stock
        )
        
        if calc_result.get("status") == "success":
            reorder_qty = calc_result.get("result")
        else:
            # Fallback or log error
            reorder_qty = 0.0
            steps.append(f"calculate_reorder_quantities error for {item.product}: {calc_result.get('message')}")
        
        restock_items.append(RestockItem(
            product=item.product,
            current_stock=item.current_stock,
            minimum_stock=threshold,
            reorder_quantity=reorder_qty
        ))
        
    state["restock_items"] = restock_items
    steps.append("calculate_reorder_quantities: Calculated quantities")
    state["execution_steps"] = steps
    return state

def generate_restock_result(state: WF001State) -> WF001State:
    restock_items = state.get("restock_items", [])
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    result = {
        "status": "success" if not errors else "completed_with_errors",
        "restock_list": [item.model_dump() for item in restock_items],
        "errors": errors
    }
    
    state["final_result"] = result
    steps.append("generate_restock_result: Completed")
    state["execution_steps"] = steps
    return state
