"""
Authentication service — resolves the current user from either a session
cookie (browser-based flow) or a Bearer token (API / programmatic access).
"""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.keycloak_service import keycloak_service
from app.auth.role_validator import role_validator
from app.auth.schemas import KeycloakUser
from app.auth.session_manager import session_manager
from app.database import SessionLocal
from app.logging import log_error

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
) -> KeycloakUser:
    """
    Resolve the authenticated user.

    Priority:
    1. Session cookie (browser-based flow)
    2. Authorization: Bearer <token> header (API / programmatic access)
    """
    # --- 1. Try session cookie ---
    cookie_value = request.cookies.get(session_manager.cookie_name)
    if cookie_value:
        session_data = session_manager.decode_session(cookie_value)
        if session_data and session_manager.is_session_active(session_data):
            return KeycloakUser(
                username=session_data["username"],
                email=session_data.get("email"),
                roles=session_data.get("roles", []),
                access_token=session_data["access_token"],
            )

    # --- 2. Try Bearer token ---
    if token:
        try:
            introspection = keycloak_service.introspect_token(token)
            if not introspection.get("active", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is inactive or expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            payload = keycloak_service.decode_access_token(token)
            roles = role_validator.extract_roles(payload)
            username = payload.get("preferred_username", payload.get("sub", "unknown"))
            return KeycloakUser(
                username=username,
                email=payload.get("email"),
                roles=roles,
                access_token=token,
            )
        except HTTPException:
            raise
        except Exception as exc:
            log_error("Bearer token validation failed", exc)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Please log in.",
        headers={"WWW-Authenticate": "Bearer"},
    )
