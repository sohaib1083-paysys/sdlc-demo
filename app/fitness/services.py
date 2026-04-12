from datetime import date

from app.database import SessionLocal, FitnessGoal as FitnessGoalModel


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_fitness_goals(username: str):
    db = next(get_db())
    return db.query(FitnessGoalModel).filter(FitnessGoalModel.username == username).all()


def create_fitness_goal(username: str, description: str, target_date: date):
    db = next(get_db())
    fitness_goal = FitnessGoalModel(
        username=username,
        description=description,
        target_date=target_date,
        progress=0,
    )
    db.add(fitness_goal)
    db.commit()


def update_fitness_goal(username: str, fitness_goal_id: int, description: str, target_date: date):
    db = next(get_db())
    fitness_goal = db.query(FitnessGoalModel).filter(FitnessGoalModel.id == fitness_goal_id).first()
    if fitness_goal:
        fitness_goal.description = description
        fitness_goal.target_date = target_date
        db.commit()


def delete_fitness_goal(username: str, fitness_goal_id: int):
    db = next(get_db())
    fitness_goal = db.query(FitnessGoalModel).filter(FitnessGoalModel.id == fitness_goal_id).first()
    if fitness_goal:
        db.delete(fitness_goal)
        db.commit()
