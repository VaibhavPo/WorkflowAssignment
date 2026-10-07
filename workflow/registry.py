from dataclasses import dataclass
from typing import Any, Callable, Dict, List

@dataclass
class WorkflowMetadata:
    workflow_id: str
    workflow_name: str
    description: str
    trigger: str
    input_requirements: List[str]
    graph_factory: Callable[[], Any]
    version: str

class WorkflowRegistry:
    def __init__(self):
        self._workflows: Dict[str, WorkflowMetadata] = {}

    def register(self, metadata: WorkflowMetadata) -> None:
        if metadata.workflow_id in self._workflows:
            raise ValueError(f"Workflow {metadata.workflow_id} is already registered.")
        self._workflows[metadata.workflow_id] = metadata

    def get_workflow(self, workflow_id: str) -> WorkflowMetadata:
        if workflow_id not in self._workflows:
            raise KeyError(f"Workflow {workflow_id} not found.")
        return self._workflows[workflow_id]

    def list_workflows(self) -> List[WorkflowMetadata]:
        return list(self._workflows.values())

# Global registry instance
registry = WorkflowRegistry()

def get_workflow(workflow_id: str) -> WorkflowMetadata:
    return registry.get_workflow(workflow_id)

def list_workflows() -> List[WorkflowMetadata]:
    return registry.list_workflows()
