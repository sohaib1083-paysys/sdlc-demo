"""
Session management for Keycloak-authenticated users.

Stores per-user session data in a signed cookie (via itsdangerous) and
enforces a configurable inactivity timeout.

Session data stored in the cookie:
  {
    "access_token":  str,
    "refresh_token": str,
    "id_token":      str,
    "username":      str,
    "email":         str,
    "roles":         list[str],
    "last_activity": float   # Unix timestamp
  }
"""

import os
import time
from typing import Optional, Dict, Any

from itsdangerous import TimestampSigner, BadSignature, SignatureExpired
import json
import base64

from app.config import keycloak_config
from app.logging import log_info, log_error

# Use the session secret from the centralized config (which reads from env vars).
_COOKIE_NAME = "sdlc_session"


class SessionManager:
    """Manages Keycloak session data stored in a signed cookie."""

    def __init__(self):
        # Secret is read lazily from config so tests can override it
        pass

    @property
    def _signer(self) -> TimestampSigner:
        return TimestampSigner(keycloak_config.session_secret_key)

    # ------------------------------------------------------------------
    # Encoding / Decoding
    # ------------------------------------------------------------------

    def encode_session(self, data: Dict[str, Any]) -> str:
        """Serialize *data* to a signed cookie value."""
        raw = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
        return self._signer.sign(raw).decode()

    _REQUIRED_SESSION_FIELDS = {"access_token", "username", "last_activity"}

    def decode_session(self, cookie_value: str) -> Optional[Dict[str, Any]]:
        """
        Verify and deserialize a cookie value.
        Returns ``None`` if the signature is invalid or required session fields
        are missing.  Activity-based expiration is checked separately via
        ``is_session_active()``.
        """
        try:
            raw = self._signer.unsign(cookie_value)
            data = json.loads(base64.urlsafe_b64decode(raw).decode())
            if not isinstance(data, dict) or not self._REQUIRED_SESSION_FIELDS.issubset(data):
                log_error(
                    "Session data is missing required fields",
                    Exception(f"Missing: {self._REQUIRED_SESSION_FIELDS - set(data)}"),
                )
                return None
            return data
        except SignatureExpired:
            log_info("Session cookie has an expired signature")
            return None
        except BadSignature:
            log_error("Invalid session cookie signature", Exception("BadSignature"))
            return None
        except Exception as exc:
            log_error("Failed to decode session cookie", exc)
            return None

    # ------------------------------------------------------------------
    # Session helpers
    # ------------------------------------------------------------------

    def create_session(
        self,
        access_token: str,
        refresh_token: str,
        id_token: str,
        username: str,
        email: str,
        roles: list,
    ) -> str:
        """Return a signed cookie value representing a new session."""
        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "id_token": id_token,
            "username": username,
            "email": email,
            "roles": roles,
            "last_activity": time.time(),
        }
        return self.encode_session(data)

    def is_session_active(self, session_data: Dict[str, Any]) -> bool:
        """
        Check whether the session is still within the inactivity timeout.
        """
        last_activity = session_data.get("last_activity", 0)
        return (time.time() - last_activity) < keycloak_config.inactivity_timeout

    def refresh_last_activity(self, session_data: Dict[str, Any]) -> str:
        """Update ``last_activity`` and return a new signed cookie value."""
        session_data["last_activity"] = time.time()
        return self.encode_session(session_data)

    @property
    def cookie_name(self) -> str:
        return _COOKIE_NAME


# Module-level singleton
session_manager = SessionManager()
