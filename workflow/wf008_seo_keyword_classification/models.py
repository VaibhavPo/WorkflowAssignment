from pydantic import BaseModel
from typing import Optional

class ClassifiedKeyword(BaseModel):
    keyword: str
    intent: str
    category: Optional[str]
    mapped_page: Optional[str]
    priority: str
