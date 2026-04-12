from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.auth.routes import auth_router
from app.config import keycloak_config
from app.fitness.routes import fitness_router

app = FastAPI(title="SDL Console")

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware — secret is read from config (KEYCLOAK_SESSION_SECRET_KEY
# env var).  max_age is not set here; inactivity-based expiration is handled
# by session_manager.py's is_session_active() check.
app.add_middleware(
    SessionMiddleware,
    secret_key=keycloak_config.session_secret_key,
    same_site="lax",
    https_only=keycloak_config.session_https_only,
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(fitness_router, prefix="/fitness", tags=["fitness"])
