from langgraph.graph import StateGraph, START, END
from .state import WF004State
from .nodes import (
    validate_attributes,
    generate_product_description,
    generate_short_description,
    generate_seo_title,
    generate_meta_description,
    generate_result
)

def create_product_description_graph():
    workflow = StateGraph(WF004State)
    
    workflow.add_node("validate_attributes", validate_attributes)
    workflow.add_node("generate_product_description", generate_product_description)
    workflow.add_node("generate_short_description", generate_short_description)
    workflow.add_node("generate_seo_title", generate_seo_title)
    workflow.add_node("generate_meta_description", generate_meta_description)
    workflow.add_node("generate_result", generate_result)
    
    workflow.add_edge(START, "validate_attributes")
    workflow.add_edge("validate_attributes", "generate_product_description")
    workflow.add_edge("generate_product_description", "generate_short_description")
    workflow.add_edge("generate_short_description", "generate_seo_title")
    workflow.add_edge("generate_seo_title", "generate_meta_description")
    workflow.add_edge("generate_meta_description", "generate_result")
    workflow.add_edge("generate_result", END)
    
    return workflow.compile()
