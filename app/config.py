from pydantic import BaseSettings

class KeycloakConfig(BaseSettings):
    """
    Keycloak configuration settings.
    """
    keycloak_url: str
    realm: str
    client_id: str
    client_secret: str

class LoggingConfig(BaseSettings):
    """
    Logging configuration settings.
    """
    log_level: str = "INFO"
    log_file: str = "app.log"

keycloak_config = KeycloakConfig()
logging_config = LoggingConfig()
