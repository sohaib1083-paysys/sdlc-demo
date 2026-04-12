from typing import Optional

from fastapi import HTTPException, Request

from app.auth.keycloak_service import keycloak_service
from app.auth.role_validator import role_validator
from app.auth.schemas import KeycloakUser
from app.auth.session_manager import session_manager
from app.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    token: Optional[str] = None,
) -> KeycloakUser:
    """
    Resolve the current user from the session cookie or a Bearer token.
    Re-exported here for backward compatibility with fitness routes.
    """
    from app.auth.routes import get_current_user as _get_current_user  # noqa: PLC0415
    from fastapi.security import OAuth2PasswordBearer  # noqa: PLC0415

    oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
    # Delegate to the canonical implementation in routes.py
    return _get_current_user(request=request, token=token)
