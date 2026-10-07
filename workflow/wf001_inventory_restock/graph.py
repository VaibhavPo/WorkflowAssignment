from langgraph.graph import StateGraph, START, END
from .state import WF001State
from .nodes import (
    load_inventory,
    validate_inventory,
    evaluate_stock,
    calculate_reorder_quantities,
    generate_restock_result
)

def create_inventory_restock_graph():
    workflow = StateGraph(WF001State)
    
    workflow.add_node("load_inventory", load_inventory)
    workflow.add_node("validate_inventory", validate_inventory)
    workflow.add_node("evaluate_stock", evaluate_stock)
    workflow.add_node("calculate_reorder_quantities", calculate_reorder_quantities)
    workflow.add_node("generate_restock_result", generate_restock_result)
    
    workflow.add_edge(START, "load_inventory")
    workflow.add_edge("load_inventory", "validate_inventory")
    workflow.add_edge("validate_inventory", "evaluate_stock")
    workflow.add_edge("evaluate_stock", "calculate_reorder_quantities")
    workflow.add_edge("calculate_reorder_quantities", "generate_restock_result")
    workflow.add_edge("generate_restock_result", END)
    
    return workflow.compile()
