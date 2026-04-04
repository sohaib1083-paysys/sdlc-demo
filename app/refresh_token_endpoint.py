from fastapi import FastAPI, Depends, HTTPException
from app.keycloak_integration import KeycloakIntegration
from app.config import keycloak_config

app = FastAPI()

@app.post("/refresh-token")
async def refresh_token(refresh_token: str):
    """
    Refresh an access token using a refresh token.
    
    Args:
    refresh_token (str): The refresh token to use.
    
    Returns:
    dict: A dictionary containing the new access token.
    """
    keycloak_integration = KeycloakIntegration()
    try:
        new_access_token = keycloak_integration.refresh_token(refresh_token)
        return {"access_token": new_access_token}
    except Exception as e:
        log_error("Error refreshing token", e)
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.post("/validate-token")
async def validate_token(token: str):
    """
    Validate an access token.
    
    Args:
    token (str): The token to validate.
    
    Returns:
    dict: A dictionary containing whether the token is valid.
    """
    keycloak_integration = KeycloakIntegration()
    try:
        is_valid = keycloak_integration.validate_token(token)
        return {"is_valid": is_valid}
    except Exception as e:
        log_error("Error validating token", e)
        raise HTTPException(status_code=401, detail="Invalid token")
