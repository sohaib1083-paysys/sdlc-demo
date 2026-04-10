from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.templates.services import get_templates

router = APIRouter()

class Template(BaseModel):
    id: int
    name: str
    description: str

@router.get("/", response_model=list[Template])
async def get_templates():
    return get_templates()
