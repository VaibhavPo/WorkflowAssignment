from typing import List, Any
from workflow.base import BaseWorkflowState

class WF006State(BaseWorkflowState):
    catalog_source: str
    catalog_records: List[Any]
    duplicate_groups: List[Any]
