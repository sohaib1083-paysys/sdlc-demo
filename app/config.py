from pydantic import BaseSettings
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

    class Config:
        env_prefix = "KEYCLOAK_"
        # Allow reading from a .env file if present
        env_file = ".env"
        env_file_encoding = "utf-8"


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
