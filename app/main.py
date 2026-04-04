# app/main.py
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import HTTPException
from app.auth.routes import auth_router
from app.workouts.routes import workout_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(workout_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

# app/auth/routes.py
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.auth.services import authenticate_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return authenticate_user(token)

# app/auth/services.py
from app.auth.models import User
from app.database import session

def authenticate_user(token: str):
    user = session.query(User).filter(User.token == token).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=401, detail="Invalid token")

# app/workouts/routes.py
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.workouts.services import log_workout, get_workouts
from app.auth.services import authenticate_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/workouts")
async def create_workout(workout: WorkoutSchema, user: User = Depends(authenticate_user)):
    return log_workout(workout, user)

@router.get("/workouts")
async def read_workouts(user: User = Depends(authenticate_user)):
    return get_workouts(user)

# app/workouts/schemas.py
from pydantic import BaseModel

class WorkoutSchema(BaseModel):
    date: str
    exercise_type: str
    duration: int
    calories_burned: int

# app/workouts/services.py
from app.workouts.models import Workout
from app.database import session

def log_workout(workout: WorkoutSchema, user: User):
    new_workout = Workout(date=workout.date, exercise_type=workout.exercise_type, duration=workout.duration, calories_burned=workout.calories_burned, user_id=user.id)
    session.add(new_workout)
    session.commit()
    return new_workout.id

def get_workouts(user: User):
    return session.query(Workout).filter(Workout.user_id == user.id).all()

# app/workouts/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.auth.models import User

Base = declarative_base()

class Workout(Base):
    __tablename__ = 'workouts'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    exercise_type = Column(String)
    duration = Column(Integer)
    calories_burned = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))

# app/auth/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    token = Column(String)

# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)

def get_session():
    return Session()

session = get_session()

# app/tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_workout():
    response = client.post("/workouts", json={"date": "2022-01-01", "exercise_type": "running", "duration": 30, "calories_burned": 200})
    assert response.status_code == 401

def test_read_workouts():
    response = client.get("/workouts")
    assert response.status_code == 401

def test_create_workout_with_token():
    token = "valid_token"
    response = client.post("/workouts", json={"date": "2022-01-01", "exercise_type": "running", "duration": 30, "calories_burned": 200}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

def test_read_workouts_with_token():
    token = "valid_token"
    response = client.get("/workouts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

# app/tests/test_auth.py
from fastapi.testclient import TestClient
from app.auth.routes import auth_router

client = TestClient(auth_router)

def test_get_token():
    response = client.get("/token")
    assert response.status_code == 401

def test_get_token_with_token():
    token = "valid_token"
    response = client.get("/token", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

# app/tests/test_workouts.py
from fastapi.testclient import TestClient
from app.workouts.routes import workout_router

client = TestClient(workout_router)

def test_create_workout():
    response = client.post("/workouts", json={"date": "2022-01-01", "exercise_type": "running", "duration": 30, "calories_burned": 200})
    assert response.status_code == 401

def test_read_workouts():
    response = client.get("/workouts")
    assert response.status_code == 401

def test_create_workout_with_token():
    token = "valid_token"
    response = client.post("/workouts", json={"date": "2022-01-01", "exercise_type": "running", "duration": 30, "calories_burned": 200}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

def test_read_workouts_with_token():
    token = "valid_token"
    response = client.get("/workouts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
