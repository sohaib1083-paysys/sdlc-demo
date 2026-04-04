from googleapiclient.discovery import build

class EmailService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.gmail_service = build('gmail', 'v1', developerKey=api_key)

    def send_email(self, message):
        message_data = {
            'raw': f'To: {message.to}\r\nSubject: {message.subject}\r\n\r\n{message.body}'
        }
        self.gmail_service.users().messages().send(userId='me', body=message_data).execute()
