from typing import List, Any, Optional
from workflow.base import BaseWorkflowState

class WF008State(BaseWorkflowState):
    keyword_source: str
    product_category_info: Optional[str]
    keyword_records: List[Any]
    deduplicated_keywords: List[Any]
    classified_keywords: List[Any]
