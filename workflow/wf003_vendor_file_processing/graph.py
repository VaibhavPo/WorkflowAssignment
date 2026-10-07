from langgraph.graph import StateGraph, START, END
from .state import WF003State
from .nodes import (
    read_vendor_file,
    validate_vendor_data,
    generate_result
)

def create_vendor_file_processing_graph():
    workflow = StateGraph(WF003State)
    
    workflow.add_node("read_vendor_file", read_vendor_file)
    workflow.add_node("validate_vendor_data", validate_vendor_data)
    workflow.add_node("generate_result", generate_result)
    
    workflow.add_edge(START, "read_vendor_file")
    workflow.add_edge("read_vendor_file", "validate_vendor_data")
    workflow.add_edge("validate_vendor_data", "generate_result")
    workflow.add_edge("generate_result", END)
    
    return workflow.compile()
