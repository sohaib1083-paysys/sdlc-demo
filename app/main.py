from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import auth_router
from app.calendar.routes import calendar_router
from app.email.routes import email_router
from app.nlp.routes import nlp_router
from app.ui.routes import ui_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(calendar_router)
app.include_router(email_router)
app.include_router(nlp_router)
app.include_router(ui_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get_root():
    return {"message": "Welcome to the Task Automation Agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
