from .state import WF009State
from .models import RankedEmployee
from tools.sqlite_db import query_sqlite
from tools.llm_generate import llm_generate

def parse_task(state: WF009State) -> WF009State:
    task_desc = state.get("task", "")
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    tasks_to_process = []
    
    import os
    import csv
    if isinstance(task_desc, str) and os.path.isfile(task_desc):
        try:
            if task_desc.lower().endswith('.csv'):
                with open(task_desc, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('status', '').lower() in ['open', '']:
                            tasks_to_process.append({
                                'task_id': row.get('task_id', f"T-{len(tasks_to_process)+1}"),
                                'description': row.get('description', ''),
                                'required_skills': row.get('required_skills', ''),
                                'priority': row.get('priority', 'normal'),
                                'deadline': row.get('deadline', 'None')
                            })
                steps.append(f"parse_task: Read {len(tasks_to_process)} open tasks from CSV")
            else:
                with open(task_desc, 'r', encoding='utf-8') as f:
                    task_desc = f.read()
                steps.append("parse_task: Read task description from file")
        except Exception as e:
            errors.append(f"Failed to read task file: {str(e)}")
            state["execution_steps"] = steps + ["parse_task: Failed to read file"]
            state["errors"] = errors
            return state

    if not tasks_to_process:
        if not task_desc:
            errors.append("Task description is missing.")
            state["execution_steps"] = steps + ["parse_task: Failed (No task provided)"]
            state["errors"] = errors
            return state
            
        tasks_to_process.append({
            'task_id': 'T-001',
            'description': task_desc,
            'required_skills': state.get('required_skills'),
            'priority': state.get('priority', 'normal'),
            'deadline': state.get('deadline', 'None')
        })
        
    for t in tasks_to_process:
        req_skills = t.get('required_skills')
        if not req_skills:
            task_instruction = "Extract a list of required technical or soft skills from the given task description."
            instructions = "Return only explicitly mentioned or highly obvious necessary skills as a list of strings."
            output_schema = {
                "type": "object",
                "properties": {
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["skills"]
            }
            
            res = llm_generate(task_instruction, instructions, t['description'], output_schema)
            
            if res.get("error"):
                errors.append(f"LLM skill extraction failed: {res.get('message')}")
                t['required_skills'] = []
            else:
                t['required_skills'] = res.get("skills", [])
        elif isinstance(req_skills, str):
            import re
            skills = re.split(r'[;,]\s*', req_skills)
            t['required_skills'] = [s.strip() for s in skills if s.strip()]
            
    state["tasks_to_process"] = tasks_to_process
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def load_employee_data(state: WF009State) -> WF009State:
    if state.get("errors"):
        return state
        
    steps = state.get("execution_steps", [])
    errors = state.get("errors", [])
    
    result = query_sqlite("SELECT * FROM employees")
    if result["status"] == "success":
        state["employee_records"] = result["data"]
        steps.append(f"load_employee_data: Loaded {len(result['data'])} employees")
    else:
        errors.append(f"Database error: {result.get('error')}")
        steps.append("load_employee_data: Failed")
        state["employee_records"] = []
        
    state["execution_steps"] = steps
    state["errors"] = errors
    return state

def rank_candidates(state: WF009State) -> WF009State:
    if state.get("errors"):
        return state
        
    # We will do ranking inside select_employee for batching
    return state

def select_employee(state: WF009State) -> WF009State:
    errors = state.get("errors", [])
    steps = state.get("execution_steps", [])
    
    if errors:
        state["final_result"] = {
            "status": "completed_with_errors",
            "errors": errors
        }
        return state
        
    tasks = state.get("tasks_to_process", [])
    employees = state.get("employee_records", [])
    assignments = []
    
    # Create a mutable working copy of employees to track workload during batch assignment
    working_employees = [dict(emp) for emp in employees]
    
    for task in tasks:
        req_skills = task.get("required_skills", [])
        priority = (task.get("priority") or "normal").lower()
        req_skills_lower = [s.strip().lower() for s in req_skills]
        
        ranked_candidates = []
        for emp in working_employees:
            emp_skills_raw = emp.get("skills", "")
            emp_skills_list = [s.strip().lower() for s in emp_skills_raw.split(",") if s.strip()]
            
            matched_skills = [s for s in req_skills_lower if s in emp_skills_list]
            skill_match = len(matched_skills) / max(1, len(req_skills_lower))
            
            workload = float(emp.get("current_workload", 0.0))
            capacity = float(emp.get("capacity", 1.0))
            capacity_score = max(0.0, (capacity - workload) / max(1.0, capacity))
            
            if priority == "high" and capacity_score < 0.3:
                capacity_score *= 0.1
                
            overall_score = (0.7 * skill_match) + (0.3 * capacity_score)
            
            if len(req_skills_lower) == 0 or skill_match > 0:
                if capacity_score > 0.05:
                    ranked_candidates.append(RankedEmployee(
                        employee_id=emp.get("employee_id"),
                        employee_name=emp.get("employee_name"),
                        matched_skills=matched_skills,
                        skill_match=skill_match,
                        capacity_score=capacity_score,
                        overall_score=overall_score
                    ))
                    
        ranked_candidates.sort(key=lambda x: x.overall_score, reverse=True)
        
        if not ranked_candidates:
            assignments.append({
                "task_id": task.get("task_id"),
                "status": "escalation_required",
                "reason": "No employee satisfies the required skill and capacity constraints."
            })
            steps.append(f"select_employee: Escalated task {task.get('task_id')} (no candidates)")
        else:
            best = ranked_candidates[0]
            assignments.append({
                "task_id": task.get("task_id"),
                "status": "assigned",
                "task": task.get("description"),
                "priority": task.get("priority"),
                "deadline": task.get("deadline"),
                "selected_employee": {
                    "employee_id": best.employee_id,
                    "name": best.employee_name
                },
                "matched_skills": best.matched_skills,
                "workload": round(1.0 - best.capacity_score, 2),
                "score": round(best.overall_score, 2),
                "reason": "Best required-skill match with sufficient capacity."
            })
            steps.append(f"select_employee: Selected {best.employee_id} for task {task.get('task_id')}")
            
            # Update working capacity (assume each task takes 0.1 capacity for simplification)
            for emp in working_employees:
                if emp.get("employee_id") == best.employee_id:
                    emp["current_workload"] = float(emp.get("current_workload", 0.0)) + 0.1
                    break
                    
    state["assignments"] = assignments
    state["final_result"] = {
        "status": "completed",
        "assignments": assignments
    }
    state["execution_steps"] = steps
    return state
