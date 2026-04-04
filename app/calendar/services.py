from googleapiclient.discovery import build

class CalendarService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.calendar_service = build('calendar', 'v3', developerKey=api_key)

    def schedule_meeting(self, event):
        event_data = {
            'summary': event.summary,
            'description': event.description,
            'start': {'dateTime': event.start},
            'end': {'dateTime': event.end},
            'attendees': [{'email': attendee} for attendee in event.attendees]
        }
        self.calendar_service.events().insert(calendarId='primary', body=event_data).execute()
