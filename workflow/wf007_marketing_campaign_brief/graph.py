from langgraph.graph import StateGraph, START, END
from .state import WF007State
from .nodes import (
    validate_inputs,
    read_product_information,
    generate_brief
)

def should_continue(state: WF007State) -> str:
    if state.get("final_result", {}).get("status") == "needs_input":
        return END
    return "read_product_information"

def create_marketing_campaign_graph():
    workflow = StateGraph(WF007State)
    
    workflow.add_node("validate_inputs", validate_inputs)
    workflow.add_node("read_product_information", read_product_information)
    workflow.add_node("generate_brief", generate_brief)
    
    workflow.add_edge(START, "validate_inputs")
    workflow.add_conditional_edges("validate_inputs", should_continue, {
        END: END,
        "read_product_information": "read_product_information"
    })
    workflow.add_edge("read_product_information", "generate_brief")
    workflow.add_edge("generate_brief", END)
    
    return workflow.compile()
