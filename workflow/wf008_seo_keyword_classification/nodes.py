from .state import WF008State
from tools.read_data import read_data
from tools.llm_generate import llm_generate
from .models import ClassifiedKeyword
import json

def load_keywords(state: WF008State) -> WF008State:
    source = state.get("keyword_source", "")
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    try:
        data = read_data(source)
        records = data.get("records", [])
        
        # Check if canonical 'keyword' column exists (or was mapped)
        if not data.get("columns", []) or "keyword" not in data.get("columns", []):
            # If not formally mapped but exists in raw data
            # read_data should have handled alias mapping.
            # Let's double check records
            has_kw = any("keyword" in r for r in records)
            if not has_kw:
                errors.append("Missing required 'keyword' column in input data.")
                steps.append("load_keywords: Failed - missing keyword column")
                state["keyword_records"] = []
            else:
                state["keyword_records"] = records
                steps.append("load_keywords: Success")
        else:
            state["keyword_records"] = records
            steps.append("load_keywords: Success")
            
    except Exception as e:
        errors.append(f"load_keywords error: {str(e)}")
        steps.append("load_keywords: Failed")
        state["keyword_records"] = []
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def deduplicate_keywords(state: WF008State) -> WF008State:
    records = state.get("keyword_records", [])
    steps = state.get("execution_steps", [])
    
    seen = set()
    deduped = []
    
    for rec in records:
        kw = rec.get("keyword")
        if not kw:
            continue
            
        # Deterministic deduplication
        normalized = str(kw).strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            rec["keyword"] = normalized  # Normalize the keyword in the record
            deduped.append(rec)
            
    state["deduplicated_keywords"] = deduped
    steps.append(f"deduplicate_keywords: Found {len(deduped)} unique keywords")
    state["execution_steps"] = steps
    return state

def classify_and_map(state: WF008State) -> WF008State:
    keywords = state.get("deduplicated_keywords", [])
    cat_info = state.get("product_category_info", "No category info provided")
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    classified_results = []
    
    if keywords:
        task = "Classify a list of SEO keywords and map them to appropriate categories/pages based on the provided category info, and determine their priority."
        instructions = (
            "Classify each keyword into exactly one of these intents: informational, commercial, transactional, navigational. "
            "Use the provided 'product_category_info' as contextual reference to map each keyword to the most relevant 'category' and recommend a 'mapped_page'. "
            "This mapping should use semantic understanding. Do not require an exact keyword-to-product match. "
            "If a keyword can be confidently mapped to a relevant category or page, provide that recommendation. "
            "If there is not enough information to make a reliable recommendation, clearly indicate that (e.g. use 'Insufficient Information') instead of inventing a specific product, category, or page. "
            "Also, identify the 'priority' (high, medium, low) using the available search volume and competition information for each keyword, applying reasonable judgment. "
            "Return a JSON object with a 'classifications' array containing the structured results."
        )
        
        input_data = {
            "keywords": keywords,
            "product_category_info": cat_info
        }
        
        output_schema = {
            "type": "object",
            "properties": {
                "classifications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "keyword": {"type": "string"},
                            "intent": {"type": "string", "enum": ["informational", "commercial", "transactional", "navigational"]},
                            "category": {"type": ["string", "null"]},
                            "mapped_page": {"type": ["string", "null"]},
                            "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                        },
                        "required": ["keyword", "intent", "category", "mapped_page", "priority"]
                    }
                }
            },
            "required": ["classifications"]
        }
        
        res = llm_generate(task, instructions, input_data, output_schema)
        
        if res.get("error"):
            errors.append(f"LLM Classification Error: {res.get('message')}")
            steps.append("classify_and_map: Failed")
        else:
            classifications = res.get("classifications", [])
            for c in classifications:
                cat = c.get("category")
                if cat in ["unmapped", "Insufficient Information"] or not cat:
                    cat = None
                
                classified_results.append(ClassifiedKeyword(
                    keyword=c.get("keyword"),
                    intent=c.get("intent"),
                    category=cat,
                    mapped_page=c.get("mapped_page"),
                    priority=c.get("priority", "low")
                ))
            steps.append(f"classify_and_map: Success for {len(classified_results)} keywords")
            
    state["classified_keywords"] = classified_results
    state["errors"] = errors
    state["execution_steps"] = steps
    return state

def generate_export(state: WF008State) -> WF008State:
    classified = state.get("classified_keywords", [])
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    result_list = [c.model_dump() for c in classified]
    
    result = {
        "status": "success" if not errors else "completed_with_errors",
        "classified_dataset": result_list,
        "summary": {
            "total_processed": len(classified),
            "high_priority": sum(1 for c in classified if c.priority == "high"),
            "mapped": sum(1 for c in classified if c.mapped_page is not None)
        },
        "errors": errors
    }
    
    state["final_result"] = result
    steps.append("generate_export: Completed")
    state["execution_steps"] = steps
    return state
