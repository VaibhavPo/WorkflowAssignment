from pydantic import BaseModel
from typing import List

class DuplicateGroup(BaseModel):
    products: List[str]
    duplicate_type: str
    confidence: float
    reason: str
