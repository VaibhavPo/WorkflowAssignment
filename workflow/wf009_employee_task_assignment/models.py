from pydantic import BaseModel
from typing import List

class RankedEmployee(BaseModel):
    employee_id: str
    employee_name: str
    matched_skills: List[str]
    skill_match: float
    capacity_score: float
    overall_score: float
