from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.auth.schemas import User

router = APIRouter()

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = User.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    return {"access_token": user.username, "token_type": "bearer"}

class User(BaseModel):
    username: str
    password: str

    @staticmethod
    def authenticate(username: str, password: str):
        # Replace with actual authentication logic
        if username == "admin" and password == "password":
            return User(username="admin", password="password")
        return None
