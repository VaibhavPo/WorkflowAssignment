from workflow.registry import WorkflowMetadata, registry
from .graph import create_inventory_restock_graph

WF001_METADATA = WorkflowMetadata(
    workflow_id="WF001",
    workflow_name="Inventory Restock Check",
    description="Identifies products whose current stock is below the minimum threshold. A global minimum_stock_threshold can be optionally provided.",
    trigger="User asks which products need restocking.",
    input_requirements=["inventory_source"],
    graph_factory=create_inventory_restock_graph,
    version="1.0"
)

registry.register(WF001_METADATA)
