from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from googleapiclient.discovery import build
from app.calendar.schemas import Event
from app.auth.routes import User

router = APIRouter()

@router.post("/schedule")
async def schedule(event: Event, user: User = Depends()):
    try:
        service = build('calendar', 'v3', developerKey="YOUR_API_KEY")
        event_data = {
            'summary': event.summary,
            'description': event.description,
            'start': {'dateTime': event.start},
            'end': {'dateTime': event.end},
            'attendees': [{'email': attendee} for attendee in event.attendees]
        }
        service.events().insert(calendarId='primary', body=event_data).execute()
        return JSONResponse(content={"message": "Event scheduled successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

class Event(BaseModel):
    summary: str
    description: str
    start: str
    end: str
    attendees: list
