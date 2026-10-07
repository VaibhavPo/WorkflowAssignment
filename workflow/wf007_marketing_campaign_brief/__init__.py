from workflow.registry import WorkflowMetadata, registry
from .graph import create_marketing_campaign_graph

WF007_METADATA = WorkflowMetadata(
    workflow_id="WF007",
    workflow_name="Marketing Campaign Brief",
    description="Generates a structured marketing campaign brief given a goal, dates, and optional product information.",
    trigger="User asks to create a marketing campaign brief, campaign strategy, or messaging.",
    input_requirements=["campaign_goal", "campaign_dates"],
    graph_factory=create_marketing_campaign_graph,
    version="1.0"
)

registry.register(WF007_METADATA)
