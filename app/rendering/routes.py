from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.rendering.services import render_video

router = APIRouter()

class Rendering(BaseModel):
    customization_id: int

@router.post("/", response_model=dict)
async def render_video(rendering: Rendering):
    return render_video(rendering)
