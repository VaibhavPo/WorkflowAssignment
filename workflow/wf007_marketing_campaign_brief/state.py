from typing import List, Any, Optional
from workflow.base import BaseWorkflowState

class WF007State(BaseWorkflowState):
    campaign_goal: Optional[str]
    campaign_dates: Optional[str]
    products_source: Optional[str]
    target_audience: Optional[str]
    promotion: Optional[str]
    
    product_records: List[Any]
    campaign_brief: Optional[dict]
