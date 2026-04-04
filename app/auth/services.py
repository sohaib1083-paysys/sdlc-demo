from app.auth.schemas import User
from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(username: str, password: str):
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if not user or user.password != password:
        return None
    return user

def get_current_user(token: str):
    db = next(get_db())
    user = db.query(User).filter(User.username == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
