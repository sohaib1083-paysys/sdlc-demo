from pydantic import BaseModel
from datetime import date

class FitnessGoal(BaseModel):
    id: int
    description: str
    target_date: date
    progress: int
