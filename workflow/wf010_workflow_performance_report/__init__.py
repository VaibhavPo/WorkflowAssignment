from workflow.registry import WorkflowMetadata, registry
from .graph import create_performance_report_graph

WF010_METADATA = WorkflowMetadata(
    workflow_id="WF010",
    workflow_name="Workflow Performance Report",
    description="Generates a report analyzing workflow execution logs, success/failure rates, execution times, and slow steps.",
    trigger="User asks which workflows are failing most often, or requests a performance report, slow workflows, execution time, failure rate, workflow errors.",
    input_requirements=["log_source"],
    graph_factory=create_performance_report_graph,
    version="1.0"
)

registry.register(WF010_METADATA)
