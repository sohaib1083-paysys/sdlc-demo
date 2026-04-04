from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import SDLCPhase
import json

app = FastAPI()

@app.get("/")
def read_root():
    with open('templates/index.html') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/sdlc_phases")
def get_sdlc_phases():
    try:
        with open('sdlc_data.json') as f:
            data = json.load(f)
        return [SDLCPhase(**phase) for phase in data]
    except FileNotFoundError:
        return {"error": "File not found"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}

app.mount("/static", StaticFiles(directory="static"), name="static")
