from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import auth_router
from app.templates.routes import templates_router
from app.customization.routes import customization_router
from app.rendering.routes import rendering_router

app = FastAPI()

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

app.include_router(auth_router, prefix="/auth")
app.include_router(templates_router, prefix="/templates")
app.include_router(customization_router, prefix="/customization")
app.include_router(rendering_router, prefix="/rendering")

@app.get("/healthcheck")
async def healthcheck():
    return JSONResponse(content={"message": "Service is healthy"}, status_code=200)
