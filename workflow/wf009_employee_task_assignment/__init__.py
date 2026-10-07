from workflow.registry import WorkflowMetadata, registry
from .graph import create_employee_assignment_graph

WF009_METADATA = WorkflowMetadata(
    workflow_id="WF009",
    workflow_name="Employee Task Assignment",
    description="Assigns a task to the most suitable employee based on required skills and available capacity/workload.",
    trigger="User asks to assign a task to the best employee, evaluate employee skills, or allocate tasks.",
    input_requirements=["task"],
    graph_factory=create_employee_assignment_graph,
    version="1.0"
)

registry.register(WF009_METADATA)
