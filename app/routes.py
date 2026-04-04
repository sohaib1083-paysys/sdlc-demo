# app/routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/hello")
async def hello_world_endpoint():
    """
    Handles GET requests to the /hello endpoint.

    Returns:
    JSONResponse: A JSON response with a 200 status code and a message.
    """
    return JSONResponse(content={"message": "Hello, World!"}, status_code=200)

@router.api_route("/hello", methods=["POST", "PUT", "DELETE"])
async def method_not_allowed_handler():
    """
    Handles non-GET requests to the /hello endpoint.

    Returns:
    JSONResponse: A JSON response with a 405 status code and an error message.
    """
    return JSONResponse(content={"error": "Method Not Allowed"}, status_code=405)
