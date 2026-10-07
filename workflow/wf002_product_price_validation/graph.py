from langgraph.graph import StateGraph, START, END
from .state import WF002State
from .nodes import (
    load_prices,
    match_products,
    compare_prices,
    generate_report
)

def create_product_price_validation_graph():
    workflow = StateGraph(WF002State)
    
    workflow.add_node("load_prices", load_prices)
    workflow.add_node("match_products", match_products)
    workflow.add_node("compare_prices", compare_prices)
    workflow.add_node("generate_report", generate_report)
    
    workflow.add_edge(START, "load_prices")
    workflow.add_edge("load_prices", "match_products")
    workflow.add_edge("match_products", "compare_prices")
    workflow.add_edge("compare_prices", "generate_report")
    workflow.add_edge("generate_report", END)
    
    return workflow.compile()
