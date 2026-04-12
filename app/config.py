import os
import warnings
from pydantic import BaseSettings, validator
from typing import Optional


class KeycloakConfig(BaseSettings):
    """
    Keycloak configuration settings.
    """
    keycloak_url: str = "http://localhost:8080"
    realm: str = "sdlc"
    client_id: str = "sdlc-console"
    client_secret: str = "change-me"
    # The URL this application is reachable at (used to build the callback URL)
    app_base_url: str = "http://localhost:8000"
    # Required Keycloak role for SDL access
    sdl_role: str = "data-engineer"
    # Inactivity timeout in seconds (default: 30 minutes)
    inactivity_timeout: int = 1800
    # Session signing secret — MUST be overridden in production via
    # the SESSION_SECRET_KEY environment variable.
    session_secret_key: str = "sdlc-session-secret-change-in-production"

    class Config:
        env_prefix = "KEYCLOAK_"
        # Allow reading from a .env file if present
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("client_secret")
    def warn_placeholder_secret(cls, v: str) -> str:
        if v == "change-me":
            warnings.warn(
                "KEYCLOAK_CLIENT_SECRET is using the default placeholder value. "
                "This MUST be overridden in production.",
                stacklevel=2,
            )
        return v

    @validator("session_secret_key")
    def warn_placeholder_session_key(cls, v: str) -> str:
        if v == "sdlc-session-secret-change-in-production":
            warnings.warn(
                "KEYCLOAK_SESSION_SECRET_KEY is using the default placeholder value. "
                "Set SESSION_SECRET_KEY or KEYCLOAK_SESSION_SECRET_KEY in production.",
                stacklevel=2,
            )
        return v


class LoggingConfig(BaseSettings):
    """
    Logging configuration settings.
    """
    log_level: str = "INFO"
    log_file: str = "app.log"
    log_rotation: str = "10 MB"

    class Config:
        env_prefix = "LOG_"
        env_file = ".env"
        env_file_encoding = "utf-8"


keycloak_config = KeycloakConfig()
logging_config = LoggingConfig()
