from pydantic import BaseModel
from typing import Optional

class MatchedProduct(BaseModel):
    sku: str
    internal_price: float
    vendor_price: float

class ValidationResult(BaseModel):
    sku: str
    internal_price: float
    vendor_price: float
    percentage_difference: float
    status: str
