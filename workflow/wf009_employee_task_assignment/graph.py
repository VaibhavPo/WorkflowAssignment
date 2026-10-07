from langgraph.graph import StateGraph, START, END
from .state import WF009State
from .nodes import (
    parse_task,
    load_employee_data,
    rank_candidates,
    select_employee
)

def create_employee_assignment_graph():
    workflow = StateGraph(WF009State)
    
    workflow.add_node("parse_task", parse_task)
    workflow.add_node("load_employee_data", load_employee_data)
    workflow.add_node("rank_candidates", rank_candidates)
    workflow.add_node("select_employee", select_employee)
    
    workflow.add_edge(START, "parse_task")
    workflow.add_edge("parse_task", "load_employee_data")
    workflow.add_edge("load_employee_data", "rank_candidates")
    workflow.add_edge("rank_candidates", "select_employee")
    workflow.add_edge("select_employee", END)
    
    return workflow.compile()
