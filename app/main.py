from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ContactForm(BaseModel):
    name: str
    email: str
    message: str

@app.get("/landing-page")
async def get_landing_page(request: Request):
    """
    Returns the landing page HTML template.
    """
    return templates.TemplateResponse("landing_page.html", {"request": request})

@app.post("/contact-form")
async def post_contact_form(name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    """
    Handles contact form submission.
    
    Args:
    name (str): The user's name.
    email (str): The user's email.
    message (str): The user's message.
    
    Returns:
    A JSON response indicating whether the form submission was successful.
    """
    try:
        # Send email
        print(f"Form submitted by {name} ({email}): {message}")
        return {"message": "Form submitted successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/contact-form/error")
async def get_contact_form_error(request: Request):
    """
    Returns the contact form error HTML template.
    """
    return templates.TemplateResponse("contact_form_error.html", {"request": request})
