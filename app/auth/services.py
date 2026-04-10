from app.auth.schemas import User

def authenticate_user(username: str, password: str):
    # Replace with actual authentication logic
    if username == "admin" and password == "password":
        return User(username=username, password=password)
    return None
