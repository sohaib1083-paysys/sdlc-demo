from pydantic import BaseModel
from datetime import date

class User(BaseModel):
    id: int
    username: str
    password: str

class FitnessGoal(BaseModel):
    id: int
    username: str
    description: str
    target_date: date
    progress: int
