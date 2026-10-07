from typing import List, Dict, Any, Optional
from workflow.base import BaseWorkflowState

class WF003State(BaseWorkflowState):
    vendor_file_source: str
    raw_records: List[Dict[str, Any]]
    valid_rows: List[Dict[str, Any]]
    invalid_rows: List[Dict[str, Any]]
    validation_summary: Dict[str, int]
    invalid_row_report: List[Dict[str, Any]]
