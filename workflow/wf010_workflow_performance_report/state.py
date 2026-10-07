from typing import List, Any
from workflow.base import BaseWorkflowState

class WF010State(BaseWorkflowState):
    log_source: str
    log_records: List[Any]
    workflow_metrics: List[Any]
    slow_steps: List[Any]
    overall_summary: dict
    recommendations: List[str]
