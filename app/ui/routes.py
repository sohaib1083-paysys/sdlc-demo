from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/chat")
async def get_chat():
    html = '''
    <html>
        <body>
            <h1>Chat Window</h1>
            <form>
                <input type="text" name="message" />
                <button type="submit">Send</button>
            </form>
        </body>
    </html>
    '''
    return HTMLResponse(content=html, status_code=200)
