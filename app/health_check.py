# app/health_check.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

router = APIRouter()

class HealthCheckResponse(BaseModel):
    """
    Response model for the health check endpoint.
    
    Attributes:
    status (str): The status of the application.
    """
    status: str

def check_database_connection() -> bool:
    """
    Checks the connection to the database.
    
    Returns:
    bool: True if the connection is successful, False otherwise.
    """
    try:
        engine = create_engine("postgresql://user:password@host:port/dbname")
        engine.connect()
        return True
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

def check_external_services() -> bool:
    """
    Checks the status of external services the application depends on.
    
    Returns:
    bool: True if the external services are healthy, False otherwise.
    """
    try:
        response = requests.get("https://example.com/health", timeout=5)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="External service is not healthy")
        return True
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

def perform_health_check() -> HealthCheckResponse:
    """
    Performs the health check by calling the above functions and returns the result.
    
    Returns:
    HealthCheckResponse: The result of the health check.
    """
    if not check_database_connection():
        raise HTTPException(status_code=500, detail="Database connection failed")
    if not check_external_services():
        raise HTTPException(status_code=500, detail="External service is not healthy")
    return HealthCheckResponse(status="healthy")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> Optional[HealthCheckResponse]:
    """
    Handles GET requests to the /health endpoint.
    
    Returns:
    HealthCheckResponse: The result of the health check.
    """
    try:
        return perform_health_check()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
