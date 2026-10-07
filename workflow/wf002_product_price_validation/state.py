from typing import List, Any, Dict
from workflow.base import BaseWorkflowState
from .models import MatchedProduct, ValidationResult

class WF002State(BaseWorkflowState):
    internal_prices_source: str
    vendor_prices_source: str
    internal_records: List[Any]
    vendor_records: List[Any]
    matched_products: List[MatchedProduct]
    unmatched_products: List[Dict[str, Any]]
    validation_results: List[ValidationResult]
