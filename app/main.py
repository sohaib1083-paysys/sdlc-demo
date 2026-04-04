from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fish_page import router as fish_page_router
from fish_species import FishSpecies

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(fish_page_router)

@app.get("/")
async def get_homepage(request: Request):
    """
    Returns the homepage of the application.
    """
    return templates.TemplateResponse("index.html", {"request": request})

class Request:
    def __init__(self):
        self.url = "http://localhost:8000"

# app/fish_page.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fish_species import FishSpecies

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/fish-page")
async def get_fish_page(request: Request):
    """
    Returns the fish page of the application.
    """
    fish_species = FishSpecies()
    species_list = fish_species.get_fish_species()
    return templates.TemplateResponse("fish_page.html", {"request": request, "species_list": species_list})

@router.get("/fish-page/search")
async def search_fish_species(request: Request, species_name: str):
    """
    Searches for a specific fish species.
    """
    fish_species = FishSpecies()
    species_details = fish_species.search_fish_species(species_name)
    if species_details:
        return templates.TemplateResponse("fish_details.html", {"request": request, "species_details": species_details})
    else:
        return templates.TemplateResponse("fish_not_found.html", {"request": request})

@router.get("/fish-page/details/{species_id}")
async def get_fish_species_details(request: Request, species_id: int):
    """
    Returns the details of a specific fish species.
    """
    fish_species = FishSpecies()
    species_details = fish_species.get_fish_species_details(species_id)
    if species_details:
        return templates.TemplateResponse("fish_details.html", {"request": request, "species_details": species_details})
    else:
        return templates.TemplateResponse("fish_not_found.html", {"request": request})

# app/fish_species.py
import requests

class FishSpecies:
    def __init__(self):
        self.api_url = "https://example.com/fish-api"

    def get_fish_species(self):
        """
        Retrieves the list of fish species from the API.
        """
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return []

    def search_fish_species(self, species_name):
        """
        Searches for a specific fish species.
        """
        try:
            response = requests.get(self.api_url, params={"name": species_name})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    def get_fish_species_details(self, species_id):
        """
        Retrieves the details of a specific fish species.
        """
        try:
            response = requests.get(self.api_url + f"/{species_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

# templates/index.html
