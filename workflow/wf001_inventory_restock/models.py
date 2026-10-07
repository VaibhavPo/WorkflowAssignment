from pydantic import BaseModel, Field
from typing import Optional

class InventoryItem(BaseModel):
    product: str
    current_stock: float
    minimum_stock: Optional[float] = None
    
class RestockItem(BaseModel):
    product: str
    current_stock: float
    minimum_stock: float
    reorder_quantity: float
