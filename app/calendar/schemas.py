from pydantic import BaseModel

class Event(BaseModel):
    summary: str
    description: str
    start: str
    end: str
    attendees: list
