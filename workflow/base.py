from typing import TypedDict, Any, List, Optional

class BaseWorkflowState(TypedDict):
    user_request: str
    errors: List[str]
    final_result: Any
    execution_steps: List[str]
