from .state import WF004State
from tools.llm_generate import llm_generate

def validate_attributes(state: WF004State) -> WF004State:
    steps = state.get("execution_steps", [])
    
    missing = []
    attributes_to_check = ["product_name", "category", "attributes", "material", "color", "target_audience"]
    for attr in attributes_to_check:
        val = state.get(attr)
        if not val or str(val).strip() == "" or str(val).lower() == "none":
            missing.append(attr)
            
    state["missing_information"] = missing
    steps.append(f"validate_attributes: Found {len(missing)} missing attributes: {missing}")
    
    state["execution_steps"] = steps
    return state

def generate_product_description(state: WF004State) -> WF004State:
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    input_data = {
        "product_name": state.get("product_name"),
        "category": state.get("category"),
        "attributes": state.get("attributes"),
        "material": state.get("material"),
        "color": state.get("color"),
        "target_audience": state.get("target_audience"),
        "missing_information": state.get("missing_information", [])
    }
    
    schema = {
        "type": "object",
        "properties": {
            "product_description": {"type": "string"}
        },
        "required": ["product_description"]
    }
    
    res = llm_generate(
        task="Generate an SEO-friendly product description.",
        instructions="Create a clear, useful product description. Use natural keyword usage without keyword stuffing. Do not invent missing product attributes. Explicitly state if some information is unavailable or missing based on the missing_information list.",
        input_data=input_data,
        output_schema=schema
    )
    
    if "error" in res:
        errors.append(f"generate_product_description error: {res['message']}")
        state["product_description"] = ""
    else:
        state["product_description"] = res.get("product_description", "")
        steps.append("generate_product_description: Success")
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def generate_short_description(state: WF004State) -> WF004State:
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    input_data = {
        "product_name": state.get("product_name"),
        "product_description": state.get("product_description"),
        "missing_information": state.get("missing_information", [])
    }
    
    schema = {
        "type": "object",
        "properties": {
            "short_description": {"type": "string"}
        },
        "required": ["short_description"]
    }
    
    res = llm_generate(
        task="Generate an SEO-friendly short description.",
        instructions="Create a short, concise description based on the provided product description. Do not invent missing attributes.",
        input_data=input_data,
        output_schema=schema
    )
    
    if "error" in res:
        errors.append(f"generate_short_description error: {res['message']}")
        state["short_description"] = ""
    else:
        state["short_description"] = res.get("short_description", "")
        steps.append("generate_short_description: Success")
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def generate_seo_title(state: WF004State) -> WF004State:
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    input_data = {
        "product_name": state.get("product_name"),
        "category": state.get("category"),
        "product_description": state.get("product_description")
    }
    
    schema = {
        "type": "object",
        "properties": {
            "seo_title": {"type": "string"}
        },
        "required": ["seo_title"]
    }
    
    res = llm_generate(
        task="Generate an SEO title for the product.",
        instructions="Create a search-friendly SEO title. Include relevant product keywords naturally. Do not invent features.",
        input_data=input_data,
        output_schema=schema
    )
    
    if "error" in res:
        errors.append(f"generate_seo_title error: {res['message']}")
        state["seo_title"] = ""
    else:
        state["seo_title"] = res.get("seo_title", "")
        steps.append("generate_seo_title: Success")
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def generate_meta_description(state: WF004State) -> WF004State:
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    input_data = {
        "seo_title": state.get("seo_title"),
        "short_description": state.get("short_description")
    }
    
    schema = {
        "type": "object",
        "properties": {
            "meta_description": {"type": "string"}
        },
        "required": ["meta_description"]
    }
    
    res = llm_generate(
        task="Generate an SEO meta description.",
        instructions="Create a compelling meta description under 160 characters. Do not invent unsupported claims.",
        input_data=input_data,
        output_schema=schema
    )
    
    if "error" in res:
        errors.append(f"generate_meta_description error: {res['message']}")
        state["meta_description"] = ""
    else:
        state["meta_description"] = res.get("meta_description", "")
        steps.append("generate_meta_description: Success")
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def generate_result(state: WF004State) -> WF004State:
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    result = {
        "status": "success" if not errors else "completed_with_errors",
        "product_description": state.get("product_description"),
        "short_description": state.get("short_description"),
        "seo_title": state.get("seo_title"),
        "meta_description": state.get("meta_description"),
        "missing_information": state.get("missing_information"),
        "errors": errors
    }
    
    state["final_result"] = result
    steps.append("generate_result: Completed")
    state["execution_steps"] = steps
    return state
