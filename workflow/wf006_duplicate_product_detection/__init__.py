from workflow.registry import WorkflowMetadata, registry
from .graph import create_duplicate_detection_graph

WF006_METADATA = WorkflowMetadata(
    workflow_id="WF006",
    workflow_name="Duplicate Product Detection",
    description="Detects duplicate products in a catalog based on SKU exact match or high similarity in attributes.",
    trigger="User asks to find duplicate products, check for duplicate catalog entries, or find similar products.",
    input_requirements=["catalog_source"],
    graph_factory=create_duplicate_detection_graph,
    version="1.0"
)

registry.register(WF006_METADATA)
