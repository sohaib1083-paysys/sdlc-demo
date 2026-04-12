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

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer

from app.auth.keycloak_service import keycloak_service
from app.auth.role_validator import role_validator
from app.auth.schemas import KeycloakUser, LoginResponse, User
from app.auth.session_manager import session_manager
from app.logging import log_error, log_info

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


# ---------------------------------------------------------------------------
# Dependency: resolve the current user from session cookie or Bearer token
# ---------------------------------------------------------------------------


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
    state = keycloak_service.generate_state(redirect_after_login=redirect)
    authorization_url = keycloak_service.build_authorization_url(state=state)
    log_info(f"Redirecting unauthenticated request to Keycloak login [{datetime.utcnow().isoformat()}]")
    return RedirectResponse(url=authorization_url)


@auth_router.get("/callback")
async def callback(
    response: Response,
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
    redirect_to = keycloak_service.extract_redirect_from_state(state or "")

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

    # Redirect to original destination with session cookie set
    redirect_response = RedirectResponse(url=redirect_to, status_code=status.HTTP_302_FOUND)
    redirect_response.set_cookie(
        key=session_manager.cookie_name,
        value=cookie_value,
        httponly=True,
        samesite="lax",
        max_age=keycloak_config_inactivity(),
    )
    return redirect_response


def keycloak_config_inactivity() -> int:
    """Return the configured inactivity timeout (avoids circular import)."""
    from app.config import keycloak_config  # noqa: PLC0415
    return keycloak_config.inactivity_timeout


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
        post_logout_redirect=f"{request.base_url}",
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
    from app.config import keycloak_config  # noqa: PLC0415

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

    import requests as _requests  # noqa: PLC0415

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
