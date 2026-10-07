from workflow.registry import WorkflowMetadata, registry
from .graph import create_vendor_file_processing_graph

WF003_METADATA = WorkflowMetadata(
    workflow_id="WF003",
    workflow_name="Vendor File Processing",
    description="Processes vendor product files, validates required fields (SKU, Product name), and produces a cleaned dataset with error reports.",
    trigger="Process this vendor spreadsheet and show invalid rows.",
    input_requirements=["vendor_file_source"],
    graph_factory=create_vendor_file_processing_graph,
    version="1.0"
)

registry.register(WF003_METADATA)
