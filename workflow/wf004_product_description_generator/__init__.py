from workflow.registry import WorkflowMetadata, registry
from .graph import create_product_description_graph

WF004_METADATA = WorkflowMetadata(
    workflow_id="WF004",
    workflow_name="Product Description Generator",
    description="Generates SEO-friendly product content including descriptions and titles based on product attributes.",
    trigger="User asks to generate product content or SEO content for a product.",
    input_requirements=["product_name", "category", "attributes", "material", "color", "target_audience"],
    graph_factory=create_product_description_graph,
    version="1.0"
)

registry.register(WF004_METADATA)
