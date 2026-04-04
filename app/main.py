# app/main.py
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """
    Handles validation errors.

    Args:
    request (Request): The incoming request.
    exc (RequestValidationError): The validation error.

    Returns:
    JSONResponse: A JSON response with a 400 status code and an error message.
    """
    return JSONResponse(content={"error": "Invalid request"}, status_code=400)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    """
    Handles 404 errors.

    Args:
    request (Request): The incoming request.
    exc (Exception): The exception.

    Returns:
    JSONResponse: A JSON response with a 404 status code and an error message.
    """
    return JSONResponse(content={"error": "Not Found"}, status_code=404)

@app.middleware("http")
async def payload_too_large_handler(request: Request, call_next):
    """
    Handles large payloads.

    Args:
    request (Request): The incoming request.
    call_next: A callable that yields the next middleware or the route handler.

    Returns:
    JSONResponse: A JSON response with a 413 status code and an error message if the payload is too large.
    """
    if request.method == "GET" and len(await request.body()) > 1024 * 1024:
        return JSONResponse(content={"error": "Payload Too Large"}, status_code=413)
    return await call_next(request)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
