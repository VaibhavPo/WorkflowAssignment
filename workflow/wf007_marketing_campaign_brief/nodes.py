from .state import WF007State
from tools.read_data import read_data
from tools.llm_generate import llm_generate

def validate_inputs(state: WF007State) -> WF007State:
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    goal = state.get("campaign_goal")
    dates = state.get("campaign_dates")
    
    missing_inputs = []
    if not goal:
        missing_inputs.append("campaign_goal")
    if not dates:
        missing_inputs.append("campaign_dates")
        
    if missing_inputs:
        state["final_result"] = {
            "status": "needs_input",
            "missing_inputs": missing_inputs,
            "message": f"Please provide the {', '.join(missing_inputs).replace('_', ' ')}."
        }
        steps.append(f"validate_inputs: Missing {missing_inputs}")
    else:
        steps.append("validate_inputs: Success")
        
    state["execution_steps"] = steps
    return state

def read_product_information(state: WF007State) -> WF007State:
    if state.get("final_result", {}).get("status") == "needs_input":
        return state
        
    source = state.get("products_source")
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    if source:
        try:
            data = read_data(source)
            state["product_records"] = data.get("records", [])
            steps.append("read_product_information: Success from file")
        except Exception as e:
            # We can still proceed without file data if not strictly required,
            # but we log the error.
            errors.append(f"Failed to read products file: {str(e)}")
            steps.append("read_product_information: Failed from file")
            state["product_records"] = []
    else:
        state["product_records"] = []
        steps.append("read_product_information: No products file provided")
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def generate_brief(state: WF007State) -> WF007State:
    if state.get("final_result", {}).get("status") == "needs_input":
        return state
        
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    task = "Create a structured marketing campaign brief based on the provided facts."
    instructions = (
        "Do NOT invent product specifications, prices, promotions, campaign dates, or product attributes. "
        "Only use the provided input facts. "
        "Return a structured JSON object with the specified schema."
    )
    
    input_data = {
        "campaign_goal": state.get("campaign_goal"),
        "campaign_dates": state.get("campaign_dates"),
        "target_audience": state.get("target_audience", "Not specified"),
        "promotion": state.get("promotion", "Not specified"),
        "products": state.get("product_records", [])
    }
    
    output_schema = {
        "type": "object",
        "properties": {
            "Campaign Objective": {"type": "string"},
            "Products": {"type": "string", "description": "Summary of the products"},
            "Target Audience": {"type": "string"},
            "Promotion": {"type": "string"},
            "Campaign Dates": {"type": "string"},
            "Key Messaging": {"type": "string"},
            "Recommended Channels": {"type": "array", "items": {"type": "string"}},
            "Campaign Checklist": {"type": "array", "items": {"type": "string"}}
        },
        "required": [
            "Campaign Objective", "Products", "Target Audience", "Promotion", 
            "Campaign Dates", "Key Messaging", "Recommended Channels", "Campaign Checklist"
        ]
    }
    
    res = llm_generate(task, instructions, input_data, output_schema)
    
    if res.get("error"):
        errors.append(f"LLM Error: {res.get('message')}")
        steps.append("generate_brief: Failed")
        state["final_result"] = {
            "status": "completed_with_errors",
            "errors": errors
        }
    else:
        state["campaign_brief"] = res
        steps.append("generate_brief: Success")
        state["final_result"] = {
            "status": "success",
            "campaign_brief": res,
            "errors": errors
        }
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state
