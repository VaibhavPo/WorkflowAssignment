from workflow.registry import WorkflowMetadata, registry
from .graph import create_seo_keyword_graph

WF008_METADATA = WorkflowMetadata(
    workflow_id="WF008",
    workflow_name="SEO Keyword Classification",
    description="Classifies SEO keywords into intents, maps them to categories, and assigns priorities.",
    trigger="User asks to classify keywords, map keywords to pages, or process SEO keywords.",
    input_requirements=["keyword_source"],
    graph_factory=create_seo_keyword_graph,
    version="1.0"
)

registry.register(WF008_METADATA)
