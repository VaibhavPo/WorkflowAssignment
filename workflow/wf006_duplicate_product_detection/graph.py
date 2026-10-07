from langgraph.graph import StateGraph, START, END
from .state import WF006State
from .nodes import (
    load_catalog,
    detect_duplicates,
    generate_result
)

def create_duplicate_detection_graph():
    workflow = StateGraph(WF006State)
    
    workflow.add_node("load_catalog", load_catalog)
    workflow.add_node("detect_duplicates", detect_duplicates)
    workflow.add_node("generate_result", generate_result)
    
    workflow.add_edge(START, "load_catalog")
    workflow.add_edge("load_catalog", "detect_duplicates")
    workflow.add_edge("detect_duplicates", "generate_result")
    workflow.add_edge("generate_result", END)
    
    return workflow.compile()
