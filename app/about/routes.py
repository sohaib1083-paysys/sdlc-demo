from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.about.models import CompanyInfo
from app.about.services import get_company_info

about_routes = APIRouter()

@about_routes.get("/about")
async def about(request: Request):
    """
    Render the about page.

    Args:
    request (Request): The incoming request.

    Returns:
    HTMLResponse: The rendered about page.
    """
    company_info = get_company_info()
    return templates.TemplateResponse("about.html", {"request": request, "company_info": company_info})
