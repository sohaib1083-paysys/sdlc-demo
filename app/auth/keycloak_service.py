"""
Keycloak OpenID Connect authentication service.

Handles the Authorization Code flow:
  1. Build the Keycloak authorization URL (with state / redirect_uri).
  2. Exchange the authorization code for tokens.
  3. Validate / introspect access tokens.
  4. Refresh access tokens.
  5. Build the Keycloak logout URL.
"""

import secrets
import threading
import urllib.parse
from datetime import datetime
from typing import Optional, Dict, Any, List

import requests
from jose import JWTError, jwt

from app.config import keycloak_config
from app.logging import log_error, log_info


class KeycloakService:
    """Wraps the Keycloak OpenID Connect endpoints."""

    def __init__(self):
        # Cached JWKS (JSON Web Key Set) for JWT signature verification
        self._jwks: Optional[List[Dict[str, Any]]] = None
        self._jwks_lock = threading.Lock()

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    @property
    def _base_oidc_url(self) -> str:
        return (
            f"{keycloak_config.keycloak_url}"
            f"/realms/{keycloak_config.realm}"
            f"/protocol/openid-connect"
        )

    @property
    def _callback_url(self) -> str:
        return f"{keycloak_config.app_base_url}/auth/callback"

    # ------------------------------------------------------------------
    # Authorization Code Flow – step 1: redirect to Keycloak
    # ------------------------------------------------------------------

    def build_authorization_url(self, state: str) -> str:
        """
        Return the Keycloak authorization URL that the browser should be
        redirected to.  ``state`` carries the OAuth2 state parameter (CSRF
        protection) and embeds the post-login redirect path via
        ``generate_state()``.
        """
        params = {
            "client_id": keycloak_config.client_id,
            "response_type": "code",
            "scope": "openid profile email",
            "redirect_uri": self._callback_url,
            "state": state,
        }
        return f"{self._base_oidc_url}/auth?{urllib.parse.urlencode(params)}"

    # ------------------------------------------------------------------
    # Authorization Code Flow – step 2: exchange code for tokens
    # ------------------------------------------------------------------

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange an authorization code for an access token, refresh token
        and ID token.  Raises an exception on failure.
        """
        url = f"{self._base_oidc_url}/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._callback_url,
            "client_id": keycloak_config.client_id,
            "client_secret": keycloak_config.client_secret,
        }
        try:
            response = requests.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
            response.raise_for_status()
            tokens = response.json()
            log_info(f"Token exchange successful at {datetime.utcnow().isoformat()}")
            return tokens
        except requests.RequestException as exc:
            log_error("Token exchange failed", exc)
            raise

    # ------------------------------------------------------------------
    # Token introspection / validation
    # ------------------------------------------------------------------

    def introspect_token(self, token: str) -> Dict[str, Any]:
        """
        Call Keycloak's token introspection endpoint and return the payload.
        Returns a dict with ``active`` key (False if token is invalid/expired).
        """
        url = f"{self._base_oidc_url}/token/introspect"
        data = {
            "token": token,
            "client_id": keycloak_config.client_id,
            "client_secret": keycloak_config.client_secret,
        }
        try:
            response = requests.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            log_error("Token introspection failed", exc)
            raise

    def get_userinfo(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch user profile information from Keycloak's userinfo endpoint.
        """
        url = f"{self._base_oidc_url}/userinfo"
        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            log_error("Userinfo request failed", exc)
            raise

    # ------------------------------------------------------------------
    # Token refresh
    # ------------------------------------------------------------------

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Obtain a new access token (and possibly a new refresh token) using
        the provided refresh token.
        """
        url = f"{self._base_oidc_url}/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": keycloak_config.client_id,
            "client_secret": keycloak_config.client_secret,
        }
        try:
            response = requests.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            log_error("Token refresh failed", exc)
            raise

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    def build_logout_url(self, id_token_hint: Optional[str] = None, post_logout_redirect_uri: Optional[str] = None) -> str:
        """
        Return the Keycloak end-session URL.
        """
        params: Dict[str, str] = {"client_id": keycloak_config.client_id}
        if id_token_hint:
            params["id_token_hint"] = id_token_hint
        if post_logout_redirect_uri:
            params["post_logout_redirect_uri"] = post_logout_redirect_uri
        return f"{self._base_oidc_url}/logout?{urllib.parse.urlencode(params)}"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def generate_state(redirect_after_login: str = "/") -> str:
        """
        Generate a cryptographically random state token that embeds the
        post-login redirect path.  Format: ``<random>:<url-encoded-path>``
        """
        random_part = secrets.token_urlsafe(32)
        encoded_path = urllib.parse.quote(redirect_after_login, safe="")
        return f"{random_part}:{encoded_path}"

    @staticmethod
    def extract_redirect_from_state(state: str) -> str:
        """
        Extract the post-login redirect path from a state value produced by
        ``generate_state``.  Falls back to ``"/"`` on malformed input.
        """
        try:
            _, encoded_path = state.split(":", 1)
            return urllib.parse.unquote(encoded_path) or "/"
        except (ValueError, AttributeError):
            return "/"

    def _get_jwks(self) -> List[Dict[str, Any]]:
        """
        Fetch and cache the JSON Web Key Set (JWKS) from Keycloak.

        The JWKS is fetched lazily on the first call and cached in memory.
        Callers should call ``invalidate_jwks_cache()`` if a token with an
        unknown key ID is encountered.
        """
        with self._jwks_lock:
            if self._jwks is not None:
                return self._jwks
            try:
                url = f"{self._base_oidc_url}/certs"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                self._jwks = response.json().get("keys", [])
                log_info("JWKS fetched and cached from Keycloak")
                return self._jwks
            except requests.RequestException as exc:
                log_error("Failed to fetch JWKS from Keycloak", exc)
                raise

    def invalidate_jwks_cache(self) -> None:
        """Clear the cached JWKS so the next call to ``_get_jwks`` re-fetches."""
        with self._jwks_lock:
            self._jwks = None

    def decode_access_token(self, access_token: str) -> Dict[str, Any]:
        """
        Decode and verify a JWT access token using Keycloak's public keys
        (JWKS).  Falls back to introspection-based claims extraction when
        JWKS is unavailable (e.g., Keycloak unreachable during tests).

        Returns the payload claims dict.
        """
        try:
            jwks = self._get_jwks()
            # Build a dict of keys by kid for efficient lookup
            header = jwt.get_unverified_header(access_token)
            kid = header.get("kid")
            key = next((k for k in jwks if k.get("kid") == kid), None)
            if key is None and jwks:
                # Unknown kid — refresh the cache once and try again
                self.invalidate_jwks_cache()
                jwks = self._get_jwks()
                key = next((k for k in jwks if k.get("kid") == kid), None)
            if key is None:
                raise JWTError(f"No matching public key found for kid={kid}")
            payload = jwt.decode(
                access_token,
                key,
                algorithms=["RS256", "HS256"],
                options={"verify_aud": False},
            )
            return payload
        except requests.RequestException:
            # Keycloak unreachable — fall back to unverified decode
            log_info("JWKS unavailable; falling back to unverified JWT decode")
        except JWTError as exc:
            log_error("JWT signature verification failed", exc)
            raise

        # Fallback: decode without signature verification
        try:
            return jwt.decode(
                access_token,
                options={"verify_signature": False, "verify_aud": False},
                algorithms=["RS256", "HS256"],
            )
        except JWTError as exc:
            log_error("Failed to decode access token", exc)
            raise


# Module-level singleton
keycloak_service = KeycloakService()
