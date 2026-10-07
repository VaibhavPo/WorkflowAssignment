from typing import List, Any, Optional
from workflow.base import BaseWorkflowState

class WF009State(BaseWorkflowState):
    task: str
    required_skills: Optional[List[str]]
    priority: Optional[str]
    deadline: Optional[str]
    
    tasks_to_process: Optional[List[dict]]
    assignments: Optional[List[dict]]
    
    employee_records: List[Any]
    ranked_candidates: List[Any]
