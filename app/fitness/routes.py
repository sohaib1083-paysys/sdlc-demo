from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.fitness.schemas import FitnessGoal
from app.fitness.services import get_fitness_goals, create_fitness_goal, update_fitness_goal, delete_fitness_goal
from app.auth.services import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/fitness-page")
async def get_fitness_page(current_user: User = Depends(get_current_user)):
    fitness_goals = get_fitness_goals(current_user.username)
    return {"fitness_goals": fitness_goals}

@router.post("/fitness-goals")
async def create_new_fitness_goal(fitness_goal: FitnessGoal, current_user: User = Depends(get_current_user)):
    create_fitness_goal(current_user.username, fitness_goal.description, fitness_goal.target_date)
    return {"message": "Fitness goal created successfully"}

@router.put("/fitness-goals/{fitness_goal_id}")
async def update_fitness_goal(fitness_goal_id: int, fitness_goal: FitnessGoal, current_user: User = Depends(get_current_user)):
    update_fitness_goal(current_user.username, fitness_goal_id, fitness_goal.description, fitness_goal.target_date)
    return {"message": "Fitness goal updated successfully"}

@router.delete("/fitness-goals/{fitness_goal_id}")
async def delete_fitness_goal(fitness_goal_id: int, current_user: User = Depends(get_current_user)):
    delete_fitness_goal(current_user.username, fitness_goal_id)
    return {"message": "Fitness goal deleted successfully"}
