from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

auth_routes = APIRouter()

@auth_routes.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@auth_routes.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
