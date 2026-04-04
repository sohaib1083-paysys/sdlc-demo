from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.auth.routes import auth_routes
from app.about.routes import about_routes
from app.errors import handle_404, handle_no_internet

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.include_router(auth_routes)
app.include_router(about_routes)

@app.exception_handler(404)
async def handle_404_error(request: Request, exc):
    return handle_404()

@app.exception_handler(Exception)
async def handle_no_internet_error(request: Request, exc):
    return handle_no_internet()
