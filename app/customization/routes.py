from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from app.customization.services import customize_video

router = APIRouter()

class Customization(BaseModel):
    template_id: int
    text: str
    image: UploadFile
    music: UploadFile

@router.post("/", response_model=dict)
async def customize_video(customization: Customization):
    return customize_video(customization)
