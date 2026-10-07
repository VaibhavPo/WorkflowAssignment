from .state import WF006State
from tools.read_data import read_data
from tools.text_similarity import calculate_similarity
from .models import DuplicateGroup

def load_catalog(state: WF006State) -> WF006State:
    source = state.get("catalog_source", "")
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    try:
        data = read_data(source)
        state["catalog_records"] = data.get("records", [])
        steps.append("load_catalog: Success")
    except Exception as e:
        errors.append(f"load_catalog error: {str(e)}")
        steps.append("load_catalog: Failed")
        state["catalog_records"] = []
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def detect_duplicates(state: WF006State) -> WF006State:
    records = state.get("catalog_records", [])
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    duplicate_groups = []
    visited = set()
    
    # Simple connected components approach for grouping
    for i, rec1 in enumerate(records):
        if i in visited:
            continue
            
        current_group = [i]
        group_type = None
        group_confidence = 0.0
        group_reason = ""
        
        for j in range(i + 1, len(records)):
            if j in visited:
                continue
                
            rec2 = records[j]
            
            sku1 = rec1.get("sku")
            sku2 = rec2.get("sku")
            
            is_definite = False
            is_possible = False
            confidence = 0.0
            reason = ""
            
            # 1. Exact SKU match
            if sku1 and sku2 and str(sku1).strip() == str(sku2).strip():
                is_definite = True
                confidence = 1.0
                reason = "Exact SKU match"
            else:
                # 2. Attribute similarity
                name1 = str(rec1.get("product_name", "") or "")
                name2 = str(rec2.get("product_name", "") or "")
                
                cat1 = str(rec1.get("category", "") or "")
                cat2 = str(rec2.get("category", "") or "")
                
                # We can combine attributes into a single string for comparison
                attr1 = f"{name1} {cat1}".strip()
                attr2 = f"{name2} {cat2}".strip()
                
                if attr1 and attr2:
                    sim = calculate_similarity(attr1, attr2)
                    if sim > 0.85:
                        is_possible = True
                        confidence = round(sim, 2)
                        reason = "High similarity in product name and attributes"
                        
            if is_definite or is_possible:
                current_group.append(j)
                visited.add(j)
                
                if is_definite:
                    group_type = "definite_duplicate"
                    group_confidence = max(group_confidence, confidence)
                    group_reason = reason
                elif not group_type:
                    group_type = "possible_duplicate"
                    group_confidence = max(group_confidence, confidence)
                    group_reason = reason
                    
        if len(current_group) > 1:
            visited.add(i)
            # Find identifiers to output (sku or product name)
            product_ids = []
            for idx in current_group:
                r = records[idx]
                pid = r.get("sku") or r.get("product_name") or f"Row-{idx+1}"
                product_ids.append(str(pid))
                
            duplicate_groups.append(DuplicateGroup(
                products=product_ids,
                duplicate_type=group_type,
                confidence=group_confidence,
                reason=group_reason
            ))
            
    state["duplicate_groups"] = duplicate_groups
    steps.append(f"detect_duplicates: Found {len(duplicate_groups)} groups")
    state["execution_steps"] = steps
    return state

def generate_result(state: WF006State) -> WF006State:
    groups = state.get("duplicate_groups", [])
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    records = state.get("catalog_records", [])
    
    definite_count = sum(1 for g in groups if g.duplicate_type == "definite_duplicate")
    possible_count = sum(1 for g in groups if g.duplicate_type == "possible_duplicate")
    
    result = {
        "status": "success" if not errors else "completed_with_errors",
        "duplicate_groups": [g.model_dump() for g in groups],
        "summary": {
            "total_products": len(records),
            "definite_duplicates": definite_count,
            "possible_duplicates": possible_count
        },
        "errors": errors
    }
    
    state["final_result"] = result
    steps.append("generate_result: Completed")
    state["execution_steps"] = steps
    return state
