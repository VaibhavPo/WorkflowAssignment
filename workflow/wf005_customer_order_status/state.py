from typing import Optional, Dict, Any
from workflow.base import BaseWorkflowState

class WF005State(BaseWorkflowState):
    order_id: Optional[str]
    customer_email: Optional[str]
    
    order_info: Optional[Dict[str, Any]]
    shipment_info: Optional[Dict[str, Any]]
    status_summary: Optional[str]
