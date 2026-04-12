from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.auth.routes import auth_router
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

# Session middleware — secret should be overridden via an environment variable
# in production (e.g. SESSION_SECRET_KEY).
app.add_middleware(
    SessionMiddleware,
    secret_key="sdlc-session-secret-change-in-production",
    max_age=1800,          # matches default inactivity timeout
    same_site="lax",
    https_only=False,      # set to True in production behind HTTPS
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(fitness_router, prefix="/fitness", tags=["fitness"])
