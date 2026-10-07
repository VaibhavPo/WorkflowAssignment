from .state import WF002State
from tools.read_data import read_data
from tools.calculate import calculate
from .models import MatchedProduct, ValidationResult

def load_prices(state: WF002State) -> WF002State:
    int_source = state.get("internal_prices_source", "")
    ven_source = state.get("vendor_prices_source", "")
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    try:
        int_data = read_data(int_source)
        state["internal_records"] = int_data.get("records", [])
        steps.append("load_prices: Loaded internal prices")
    except Exception as e:
        errors.append(f"load_prices internal error: {str(e)}")
        state["internal_records"] = []
        
    try:
        ven_data = read_data(ven_source)
        state["vendor_records"] = ven_data.get("records", [])
        steps.append("load_prices: Loaded vendor prices")
    except Exception as e:
        errors.append(f"load_prices vendor error: {str(e)}")
        state["vendor_records"] = []
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def match_products(state: WF002State) -> WF002State:
    int_records = state.get("internal_records", [])
    ven_records = state.get("vendor_records", [])
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    int_dict = {}
    for r in int_records:
        if isinstance(r, dict) and "sku" in r:
            int_dict[str(r["sku"])] = r
            
    ven_dict = {}
    for r in ven_records:
        if isinstance(r, dict) and "sku" in r:
            ven_dict[str(r["sku"])] = r
            
    matched = []
    unmatched = []
    
    all_skus = set(int_dict.keys()).union(set(ven_dict.keys()))
    for sku in all_skus:
        if sku in int_dict and sku in ven_dict:
            try:
                ip = float(int_dict[sku].get("price", 0))
                vp = float(ven_dict[sku].get("price", 0))
                if ip <= 0:
                    errors.append(f"Invalid internal price for SKU {sku}")
                    unmatched.append({"sku": sku, "reason": "Invalid internal price", "source": "internal"})
                    continue
                if vp < 0:
                    errors.append(f"Invalid vendor price for SKU {sku}")
                    unmatched.append({"sku": sku, "reason": "Invalid vendor price", "source": "vendor"})
                    continue
                matched.append(MatchedProduct(sku=sku, internal_price=ip, vendor_price=vp))
            except (ValueError, TypeError):
                errors.append(f"Invalid price data for SKU {sku}")
                unmatched.append({"sku": sku, "reason": "Invalid price data"})
        else:
            source = "internal" if sku in int_dict else "vendor"
            unmatched.append({"sku": sku, "reason": "Missing on one side", "source": source})
            
    state["matched_products"] = matched
    state["unmatched_products"] = unmatched
    steps.append(f"match_products: Matched {len(matched)}, Unmatched {len(unmatched)}")
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def compare_prices(state: WF002State) -> WF002State:
    matched = state.get("matched_products", [])
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    results = []
    for item in matched:
        calc = calculate("percentage_difference", current=item.vendor_price, base=item.internal_price)
        
        if calc.get("status") == "success":
            diff = abs(calc.get("result"))
        else:
            diff = 0.0
            errors.append(f"compare_prices error for SKU {item.sku}: {calc.get('message')}")
            
        thresh_calc = calculate("threshold_comparison", value=diff, threshold=10.0, operator=">")
        
        status = "FLAG"
        if thresh_calc.get("status") == "success" and thresh_calc.get("result") is False:
            status = "PASS"
            
        results.append(ValidationResult(
            sku=item.sku,
            internal_price=item.internal_price,
            vendor_price=item.vendor_price,
            percentage_difference=diff,
            status=status
        ))
        
    state["validation_results"] = results
    steps.append(f"compare_prices: Compared {len(results)} products")
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def generate_report(state: WF002State) -> WF002State:
    results = state.get("validation_results", [])
    unmatched = state.get("unmatched_products", [])
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    flags = [r for r in results if r.status == "FLAG"]
    passes = [r for r in results if r.status == "PASS"]
    
    result_data = {
        "status": "success" if not errors else "completed_with_errors",
        "summary": {
            "total_matched": len(results),
            "total_flags": len(flags),
            "total_passes": len(passes),
            "total_unmatched": len(unmatched)
        },
        "flags": [r.model_dump() for r in flags],
        "passes": [r.model_dump() for r in passes],
        "unmatched": unmatched,
        "errors": errors
    }
    
    state["final_result"] = result_data
    steps.append("generate_report: Generated validation report")
    state["execution_steps"] = steps
    return state
