from langgraph.graph import StateGraph, START, END
from .state import WF005State
from .nodes import (
    validate_identifier,
    search_order,
    search_shipment,
    summarize_status,
    generate_result
)

def create_order_status_graph():
    workflow = StateGraph(WF005State)
    
    workflow.add_node("validate_identifier", validate_identifier)
    workflow.add_node("search_order", search_order)
    workflow.add_node("search_shipment", search_shipment)
    workflow.add_node("summarize_status", summarize_status)
    workflow.add_node("generate_result", generate_result)
    
    workflow.add_edge(START, "validate_identifier")
    workflow.add_edge("validate_identifier", "search_order")
    workflow.add_edge("search_order", "search_shipment")
    workflow.add_edge("search_shipment", "summarize_status")
    workflow.add_edge("summarize_status", "generate_result")
    workflow.add_edge("generate_result", END)
    
    return workflow.compile()
