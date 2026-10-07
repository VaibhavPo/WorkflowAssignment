from .state import WF005State
from tools.sqlite_db import query_sqlite

def validate_identifier(state: WF005State) -> WF005State:
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    order_id = state.get("order_id")
    customer_email = state.get("customer_email")
    
    if not order_id and not customer_email:
        errors.append("No order ID or customer email provided. Please provide an identifier.")
        steps.append("validate_identifier: Failed - missing identifier")
    else:
        steps.append("validate_identifier: Success")
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def search_order(state: WF005State) -> WF005State:
    # If there's an error from validation, skip
    if state.get("errors"):
        return state
        
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    order_id = state.get("order_id")
    customer_email = state.get("customer_email")
    
    query = "SELECT * FROM orders WHERE "
    params = []
    
    if order_id and customer_email:
        query += "order_id = ? AND customer_email = ?"
        params = [order_id, customer_email]
    elif order_id:
        query += "order_id = ?"
        params = [order_id]
    else:
        query += "customer_email = ?"
        params = [customer_email]
        
    res = query_sqlite(query, tuple(params))
    
    if res.get("status") == "error":
        errors.append(f"Database error: {res.get('error')}")
        steps.append("search_order: Failed due to DB error")
    else:
        data = res.get("data", [])
        if not data:
            errors.append(f"No order found for the provided identifier. Please ask for another identifier.")
            steps.append("search_order: Order not found")
        else:
            state["order_info"] = data[0]
            steps.append("search_order: Order found")
            
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def search_shipment(state: WF005State) -> WF005State:
    # Skip if order not found
    if not state.get("order_info") or state.get("errors"):
        return state
        
    steps = state.get("execution_steps", [])
    
    order_id = state.get("order_info").get("order_id")
    
    res = query_sqlite("SELECT * FROM shipments WHERE order_id = ?", (order_id,))
    
    if res.get("status") == "success":
        data = res.get("data", [])
        if data:
            state["shipment_info"] = data[0]
            steps.append("search_shipment: Shipment found")
        else:
            steps.append("search_shipment: No shipment info available")
    else:
        steps.append(f"search_shipment: Error querying shipment - {res.get('error')}")
        
    state["execution_steps"] = steps
    return state

def summarize_status(state: WF005State) -> WF005State:
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    if errors:
        state["status_summary"] = " | ".join(errors)
        steps.append("summarize_status: Returning errors")
    elif state.get("order_info"):
        order = state.get("order_info")
        shipment = state.get("shipment_info")
        
        summary = f"Order {order.get('order_id')} for {order.get('customer_name')} is currently {order.get('order_status')}."
        
        if shipment:
            summary += f" Shipment status is {shipment.get('shipment_status')} via {shipment.get('carrier')}. Estimated delivery: {shipment.get('estimated_delivery')}. Tracking: {shipment.get('tracking_number')}."
        else:
            summary += " Shipment/tracking information is currently unavailable."
            
        state["status_summary"] = summary
        steps.append("summarize_status: Summary generated")
        
    state["execution_steps"] = steps
    return state

def generate_result(state: WF005State) -> WF005State:
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    result = {
        "status": "success" if not errors else "completed_with_errors",
        "order_info": state.get("order_info"),
        "shipment_info": state.get("shipment_info"),
        "status_summary": state.get("status_summary"),
        "errors": errors
    }
    
    state["final_result"] = result
    steps.append("generate_result: Completed")
    state["execution_steps"] = steps
    return state
