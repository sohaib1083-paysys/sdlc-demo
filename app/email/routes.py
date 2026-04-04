from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from googleapiclient.discovery import build
from app.email.schemas import Message
from app.auth.routes import User

router = APIRouter()

@router.post("/send")
async def send(message: Message, user: User = Depends()):
    try:
        service = build('gmail', 'v1', developerKey="YOUR_API_KEY")
        message_data = {
            'raw': f'To: {message.to}\r\nSubject: {message.subject}\r\n\r\n{message.body}'
        }
        service.users().messages().send(userId='me', body=message_data).execute()
        return JSONResponse(content={"message": "Email sent successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

class Message(BaseModel):
    to: str
    subject: str
    body: str
