from langgraph.graph import StateGraph, START, END
from .state import WF008State
from .nodes import (
    load_keywords,
    deduplicate_keywords,
    classify_and_map,
    generate_export
)

def create_seo_keyword_graph():
    workflow = StateGraph(WF008State)
    
    workflow.add_node("load_keywords", load_keywords)
    workflow.add_node("deduplicate_keywords", deduplicate_keywords)
    workflow.add_node("classify_and_map", classify_and_map)
    workflow.add_node("generate_export", generate_export)
    
    workflow.add_edge(START, "load_keywords")
    workflow.add_edge("load_keywords", "deduplicate_keywords")
    workflow.add_edge("deduplicate_keywords", "classify_and_map")
    workflow.add_edge("classify_and_map", "generate_export")
    workflow.add_edge("generate_export", END)
    
    return workflow.compile()
