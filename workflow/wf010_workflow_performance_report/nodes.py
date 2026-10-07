from .state import WF010State
from tools.read_data import read_data
from tools.calculate import calculate
from tools.llm_generate import llm_generate
from collections import defaultdict

FAILURE_RATE_THRESHOLD = 10.0
AVERAGE_EXECUTION_TIME_THRESHOLD = 5.0 # Example configurable threshold (seconds)

def load_workflow_logs(state: WF010State) -> WF010State:
    source = state.get("log_source", "")
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    try:
        data = read_data(source)
        records = data.get("records", [])
        
        cols = data.get("columns", [])
        if not cols or "workflow_id" not in cols:
            errors.append("Missing required 'workflow_id' column in input data.")
            steps.append("load_workflow_logs: Failed - missing workflow_id")
            state["log_records"] = []
        else:
            state["log_records"] = records
            steps.append("load_workflow_logs: Success")
            
    except Exception as e:
        errors.append(f"load_workflow_logs error: {str(e)}")
        steps.append("load_workflow_logs: Failed")
        state["log_records"] = []
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def calculate_metrics(state: WF010State) -> WF010State:
    records = state.get("log_records", [])
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    if not records:
        return state
        
    wf_stats = defaultdict(lambda: {"total": 0, "failures": 0, "times": [], "errors": defaultdict(int)})
    step_stats = defaultdict(lambda: {"total": 0, "times": []})
    
    overall_total = 0
    overall_failed = 0
    
    has_step_info = False
    
    for rec in records:
        wf_id = str(rec.get("workflow_id", "")).strip()
        if not wf_id: continue
        
        status = str(rec.get("execution_status", "")).strip().lower()
        time_val = rec.get("execution_time")
        err_msg = str(rec.get("error_message", "")).strip()
        step = str(rec.get("step_name", "")).strip()
        
        is_failure = (status in ["failed", "error", "completed_with_errors"])
        
        try:
            t = float(time_val) if time_val is not None else 0.0
        except ValueError:
            t = 0.0
            
        wf_stats[wf_id]["total"] += 1
        wf_stats[wf_id]["times"].append(t)
        overall_total += 1
        
        if is_failure:
            wf_stats[wf_id]["failures"] += 1
            overall_failed += 1
            if err_msg:
                wf_stats[wf_id]["errors"][err_msg] += 1
                
        if step:
            has_step_info = True
            step_key = f"{wf_id}::{step}"
            step_stats[step_key]["total"] += 1
            step_stats[step_key]["times"].append(t)
            
    workflow_metrics = []
    for wf_id, stats in wf_stats.items():
        # Use calculate tool for rates and averages
        total = stats["total"]
        failures = stats["failures"]
        
        fail_res = calculate("failure rate", total=total, failures=failures)
        fail_rate = (fail_res["result"] * 100.0) if fail_res["status"] == "success" else 0.0
        
        avg_res = calculate("average", values=stats["times"] if stats["times"] else [0.0])
        avg_time = avg_res["result"] if avg_res["status"] == "success" else 0.0
        
        flagged = (fail_rate > FAILURE_RATE_THRESHOLD) or (avg_time > AVERAGE_EXECUTION_TIME_THRESHOLD)
        
        freq_errors = [{"error": k, "count": v} for k, v in sorted(stats["errors"].items(), key=lambda x: x[1], reverse=True)[:3]]
        
        workflow_metrics.append({
            "workflow_id": wf_id,
            "total_executions": total,
            "failure_rate": fail_rate,
            "average_execution_time": avg_time,
            "flagged": flagged,
            "frequent_errors": freq_errors
        })
        
    slow_steps = []
    if has_step_info:
        for sk, s_stats in step_stats.items():
            avg_res = calculate("average", values=s_stats["times"] if s_stats["times"] else [0.0])
            avg_t = avg_res["result"] if avg_res["status"] == "success" else 0.0
            parts = sk.split("::", 1)
            slow_steps.append({
                "workflow_id": parts[0],
                "step": parts[1],
                "execution_count": s_stats["total"],
                "average_duration": avg_t
            })
        slow_steps.sort(key=lambda x: x["average_duration"], reverse=True)
        # Keep top 10 slowest
        slow_steps = slow_steps[:10]
        
    state["workflow_metrics"] = workflow_metrics
    state["slow_steps"] = slow_steps
    state["overall_summary"] = {
        "total_executions": overall_total,
        "successful": overall_total - overall_failed,
        "failed": overall_failed
    }
    steps.append("calculate_metrics: Success")
    
    state["execution_steps"] = steps
    return state

def generate_recommendations(state: WF010State) -> WF010State:
    metrics = state.get("workflow_metrics", [])
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    flagged = [m for m in metrics if m["flagged"]]
    
    if flagged:
        task = "Generate actionable recommendations based on the provided workflow performance metrics."
        instructions = (
            "Only use the provided calculated metrics and frequent errors. "
            "Do NOT invent evidence. Do NOT invent workflow IDs or errors. "
            "Provide 1-3 concise recommendations based on the data."
        )
        
        input_data = {"flagged_workflows": flagged}
        output_schema = {
            "type": "object",
            "properties": {
                "recommendations": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["recommendations"]
        }
        
        res = llm_generate(task, instructions, input_data, output_schema)
        
        if res.get("error"):
            errors.append(f"LLM Recommendation Error: {res.get('message')}")
            steps.append("generate_recommendations: Failed")
            state["recommendations"] = []
        else:
            state["recommendations"] = res.get("recommendations", [])
            steps.append("generate_recommendations: Success")
    else:
        state["recommendations"] = ["All workflows are performing within normal thresholds. No immediate action required."]
        steps.append("generate_recommendations: No flagged workflows")
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def generate_report(state: WF010State) -> WF010State:
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    result = {
        "status": "success" if not errors else "completed_with_errors",
        "overall_summary": state.get("overall_summary", {}),
        "workflow_metrics": state.get("workflow_metrics", []),
        "slow_steps": state.get("slow_steps", []) if state.get("slow_steps") else "step-level timing unavailable",
        "recommendations": state.get("recommendations", []),
        "errors": errors
    }
    
    state["final_result"] = result
    steps.append("generate_report: Completed")
    state["execution_steps"] = steps
    return state
