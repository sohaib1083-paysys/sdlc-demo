"""
Authentication routes — Keycloak OpenID Connect Authorization Code Flow.

Endpoints
---------
GET  /auth/login      – Redirects the browser to the Keycloak login page.
GET  /auth/callback   – Keycloak redirect-back handler; exchanges code for tokens,
                        validates role, sets session cookie, and redirects the
                        browser to the original destination.
GET  /auth/logout     – Clears the session cookie and redirects to Keycloak logout.
GET  /auth/me         – Returns the current authenticated user's profile.
POST /auth/token      – Legacy endpoint: validate a Bearer token passed directly.
"""

import urllib.parse
from datetime import datetime
from typing import Optional

import requests as _requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.auth.keycloak_service import keycloak_service
from app.auth.role_validator import role_validator
from app.auth.schemas import KeycloakUser, LoginResponse, User
from app.auth.services import get_current_user
from app.auth.session_manager import session_manager
from app.config import keycloak_config
from app.logging import log_error, log_info

auth_router = APIRouter()


def _safe_redirect_path(url: str) -> str:
    """
    Validate and sanitize a redirect URL so that only relative paths within
    this application are accepted.  Any scheme or host component is stripped,
    preventing open-redirect attacks.

    Returns a path that always starts with ``/``.
    """
    parsed = urllib.parse.urlparse(url)
    # Allow only relative paths (no scheme, no netloc)
    if parsed.scheme or parsed.netloc:
        return "/"
    path = parsed.path or "/"
    # Ensure the path starts with /
    if not path.startswith("/"):
        path = "/" + path
    return path


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@auth_router.get("/login")
async def login(request: Request, redirect: str = "/"):
    """
    Start the Keycloak Authorization Code Flow.

    Redirects the browser to the Keycloak login page.  The ``redirect``
    query-parameter holds the original destination and is encoded into the
    OAuth2 ``state`` value so it survives the round-trip.
    """
    # Validate the redirect parameter to prevent open-redirect attacks
    safe_redirect = _safe_redirect_path(redirect)
    state = keycloak_service.generate_state(redirect_after_login=safe_redirect)
    authorization_url = keycloak_service.build_authorization_url(state=state)
    log_info(f"Redirecting unauthenticated request to Keycloak login [{datetime.utcnow().isoformat()}]")
    return RedirectResponse(url=authorization_url)


@auth_router.get("/callback")
async def callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    """
    Handle the Keycloak redirect-back after the user has authenticated.

    Steps:
    1. Exchange the authorization code for tokens.
    2. Decode and validate the access token.
    3. Enforce role-based access (SDL role required).
    4. Create a signed session cookie.
    5. Redirect the browser to the original destination.
    """
    # Keycloak reported an error (e.g. user cancelled login)
    if error:
        msg = error_description or error
        log_error(
            f"Keycloak authentication error at {datetime.utcnow().isoformat()}",
            Exception(msg),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {msg}",
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is missing from callback.",
        )

    # Determine where to redirect after successful login
    # Validate to prevent open-redirect attacks (must be a relative path)
    raw_redirect = keycloak_service.extract_redirect_from_state(state or "")
    redirect_to = _safe_redirect_path(raw_redirect)

    # Exchange the code for tokens
    try:
        tokens = keycloak_service.exchange_code_for_tokens(code)
    except Exception as exc:
        log_error(
            f"Token exchange failed at {datetime.utcnow().isoformat()}",
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to obtain tokens from Keycloak.",
        )

    access_token = tokens.get("access_token", "")
    refresh_token = tokens.get("refresh_token", "")
    id_token = tokens.get("id_token", "")

    # Decode claims from the access token
    try:
        payload = keycloak_service.decode_access_token(access_token)
    except Exception as exc:
        log_error("Failed to decode access token in callback", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Received an invalid token from Keycloak.",
        )

    username = payload.get("preferred_username", payload.get("sub", "unknown"))
    email = payload.get("email", "")
    roles = role_validator.extract_roles(payload)

    # Enforce SDL role
    try:
        role_validator.require_role(roles, username=username)
    except HTTPException:
        log_error(
            f"Login rejected for '{username}' at {datetime.utcnow().isoformat()} — insufficient role",
            Exception("InsufficientRole"),
        )
        raise

    # Create session cookie
    cookie_value = session_manager.create_session(
        access_token=access_token,
        refresh_token=refresh_token,
        id_token=id_token,
        username=username,
        email=email,
        roles=roles,
    )

    log_info(
        f"Login successful for user '{username}' ({email}) at {datetime.utcnow().isoformat()}"
    )

    # Redirect to original destination with session cookie set.
    # Use the configured app_base_url (not request.base_url) to prevent
    # Host header injection attacks.
    base = keycloak_config.app_base_url.rstrip("/")
    full_redirect_url = base + redirect_to
    redirect_response = RedirectResponse(url=full_redirect_url, status_code=status.HTTP_302_FOUND)
    redirect_response.set_cookie(
        key=session_manager.cookie_name,
        value=cookie_value,
        httponly=True,
        samesite="lax",
        # No max_age — expiration is governed by the last_activity timestamp
        # checked in session_manager.is_session_active(), not by the cookie TTL.
    )
    return redirect_response


@auth_router.get("/logout")
async def logout(
    request: Request,
    current_user: KeycloakUser = Depends(get_current_user),
):
    """
    Log out the current user.

    Clears the session cookie and redirects the browser to Keycloak's
    end-session endpoint so the Keycloak session is also terminated.
    """
    # Retrieve id_token from session (needed for Keycloak logout hint)
    id_token = None
    cookie_value = request.cookies.get(session_manager.cookie_name)
    if cookie_value:
        session_data = session_manager.decode_session(cookie_value)
        if session_data:
            id_token = session_data.get("id_token")

    log_info(f"Logout initiated for user '{current_user.username}' at {datetime.utcnow().isoformat()}")

    logout_url = keycloak_service.build_logout_url(
        id_token_hint=id_token,
        # Use the configured app_base_url (not request.base_url) to prevent
        # Host header injection attacks.
        post_logout_redirect_uri=keycloak_config.app_base_url,
    )
    response = RedirectResponse(url=logout_url)
    response.delete_cookie(key=session_manager.cookie_name)
    return response


@auth_router.get("/me", response_model=LoginResponse)
async def get_me(current_user: KeycloakUser = Depends(get_current_user)):
    """
    Return the currently authenticated user's profile and a confirmation
    message suitable for display in the console header.
    """
    return LoginResponse(
        message=f"Welcome, {current_user.username}! You are successfully logged in.",
        username=current_user.username,
        email=current_user.email,
        roles=current_user.roles,
    )


@auth_router.post("/token")
async def login_for_access_token(user: User):
    """
    Legacy / programmatic endpoint.

    Exchanges username + password for a Keycloak access token using the
    Resource Owner Password Credentials grant.  Prefer the browser-based
    Authorization Code Flow (/auth/login) for interactive use.
    """
    url = (
        f"{keycloak_config.keycloak_url}"
        f"/realms/{keycloak_config.realm}"
        f"/protocol/openid-connect/token"
    )
    data = {
        "grant_type": "password",
        "username": user.username,
        "password": user.password,
        "client_id": keycloak_config.client_id,
        "client_secret": keycloak_config.client_secret,
        "scope": "openid",
    }

    try:
        resp = _requests.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
    except Exception as exc:
        log_error(
            f"Keycloak login attempt failed for '{user.username}' at {datetime.utcnow().isoformat()}",
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Keycloak authentication service unavailable.",
        )

    if resp.status_code != 200:
        log_error(
            f"Invalid credentials for '{user.username}' at {datetime.utcnow().isoformat()}",
            Exception(resp.text),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = resp.json()
    access_token = tokens.get("access_token", "")

    payload = keycloak_service.decode_access_token(access_token)
    roles = role_validator.extract_roles(payload)
    role_validator.require_role(roles, username=user.username)

    log_info(f"Successful token login for '{user.username}' at {datetime.utcnow().isoformat()}")
    return {"access_token": access_token, "token_type": "bearer"}
