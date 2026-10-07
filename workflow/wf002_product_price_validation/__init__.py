from workflow.registry import WorkflowMetadata, registry
from .graph import create_product_price_validation_graph

WF002_METADATA = WorkflowMetadata(
    workflow_id="WF002",
    workflow_name="Product Price Validation",
    description="Validates vendor prices against internal prices and flags discrepancies exceeding 10%.",
    trigger="Find products where vendor price differs by more than 10%.",
    input_requirements=["internal_prices_source", "vendor_prices_source"],
    graph_factory=create_product_price_validation_graph,
    version="1.0"
)

registry.register(WF002_METADATA)
