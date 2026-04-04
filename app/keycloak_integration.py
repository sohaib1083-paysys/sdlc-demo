import requests
from app.config import keycloak_config
from app.logging import log_error, log_info

class KeycloakIntegration:
    """
    Keycloak integration class.
    """
    def __init__(self):
        self.keycloak_config = keycloak_config

    def refresh_token(self, refresh_token: str):
        """
        Refresh an access token using a refresh token.
        
        Args:
        refresh_token (str): The refresh token to use.
        
        Returns:
        str: The new access token.
        """
        try:
            url = f"{self.keycloak_config.keycloak_url}/realms/{self.keycloak_config.realm}/protocol/openid-connect/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.keycloak_config.client_id,
                "client_secret": self.keycloak_config.client_secret
            }
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                log_error("Failed to refresh token", Exception(response.text))
                raise Exception("Failed to refresh token")
        except Exception as e:
            log_error("Error refreshing token", e)
            raise

    def validate_token(self, token: str):
        """
        Validate an access token.
        
        Args:
        token (str): The token to validate.
        
        Returns:
        bool: Whether the token is valid.
        """
        try:
            url = f"{self.keycloak_config.keycloak_url}/realms/{self.keycloak_config.realm}/protocol/openid-connect/token/introspect"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "token": token,
                "client_id": self.keycloak_config.client_id,
                "client_secret": self.keycloak_config.client_secret
            }
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                return response.json()["active"]
            else:
                log_error("Failed to validate token", Exception(response.text))
                raise Exception("Failed to validate token")
        except Exception as e:
            log_error("Error validating token", e)
            raise
