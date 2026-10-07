from typing import List, Optional, Any
from workflow.base import BaseWorkflowState
from .models import InventoryItem, RestockItem

class WF001State(BaseWorkflowState):
    inventory_source: str
    minimum_stock_threshold: Optional[float]
    inventory_records: List[Any]  # Raw records before validation
    valid_inventory_items: List[InventoryItem]
    low_stock_items: List[InventoryItem]
    restock_items: List[RestockItem]
