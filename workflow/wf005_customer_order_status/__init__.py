from workflow.registry import WorkflowMetadata, registry
from .graph import create_order_status_graph

WF005_METADATA = WorkflowMetadata(
    workflow_id="WF005",
    workflow_name="Customer Order Status",
    description="Retrieves order and shipment status based on order ID or customer email.",
    trigger="User asks for order status, where is my order, etc.",
    input_requirements=["order_id", "customer_email"],
    graph_factory=create_order_status_graph,
    version="1.0"
)

registry.register(WF005_METADATA)
