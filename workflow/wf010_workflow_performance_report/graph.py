from langgraph.graph import StateGraph, START, END
from .state import WF010State
from .nodes import (
    load_workflow_logs,
    calculate_metrics,
    generate_recommendations,
    generate_report
)

def create_performance_report_graph():
    workflow = StateGraph(WF010State)
    
    workflow.add_node("load_workflow_logs", load_workflow_logs)
    workflow.add_node("calculate_metrics", calculate_metrics)
    workflow.add_node("generate_recommendations", generate_recommendations)
    workflow.add_node("generate_report", generate_report)
    
    workflow.add_edge(START, "load_workflow_logs")
    workflow.add_edge("load_workflow_logs", "calculate_metrics")
    workflow.add_edge("calculate_metrics", "generate_recommendations")
    workflow.add_edge("generate_recommendations", "generate_report")
    workflow.add_edge("generate_report", END)
    
    return workflow.compile()
