"""
Role-based access control (RBAC) using Keycloak roles.

Validates that an authenticated user holds the required role to access
SDL features.  The required role is configurable via ``KeycloakConfig``.
"""

from typing import List

from fastapi import HTTPException, status

from app.config import keycloak_config
from app.logging import log_info, log_error


class RoleValidator:
    """Validates Keycloak roles against SDL access requirements."""

    def __init__(self, required_role: str = None):
        self._required_role = required_role or keycloak_config.sdl_role

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_roles(self, token_payload: dict) -> List[str]:
        """
        Extract realm-level roles from the decoded Keycloak JWT payload.

        Keycloak embeds realm roles under ``realm_access.roles`` and
        client-specific roles under ``resource_access.<client_id>.roles``.
        Both are collected and returned as a flat list.
        """
        roles: List[str] = []

        # Realm-level roles
        realm_access = token_payload.get("realm_access", {})
        roles.extend(realm_access.get("roles", []))

        # Client-level roles
        resource_access = token_payload.get("resource_access", {})
        client_roles = resource_access.get(keycloak_config.client_id, {})
        roles.extend(client_roles.get("roles", []))

        return roles

    def has_required_role(self, roles: List[str]) -> bool:
        """Return ``True`` if *roles* contains the required SDL role."""
        return self._required_role in roles

    def require_role(self, roles: List[str], username: str = "unknown") -> None:
        """
        Raise an ``HTTP 403 Forbidden`` exception if the user does not hold
        the required SDL role.
        """
        if not self.has_required_role(roles):
            log_error(
                f"Access denied for user '{username}' — missing role '{self._required_role}'",
                Exception("InsufficientRole"),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied. The role '{self._required_role}' is required "
                    "to access SDL features."
                ),
            )
        log_info(f"Role validation passed for user '{username}'")


# Module-level singleton
role_validator = RoleValidator()
