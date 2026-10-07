from typing import Optional, List, Dict, Any
from workflow.base import BaseWorkflowState

class WF004State(BaseWorkflowState):
    product_name: Optional[str]
    category: Optional[str]
    attributes: Optional[str]
    material: Optional[str]
    color: Optional[str]
    target_audience: Optional[str]
    
    missing_information: List[str]
    product_description: Optional[str]
    short_description: Optional[str]
    seo_title: Optional[str]
    meta_description: Optional[str]
