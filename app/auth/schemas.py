from typing import List, Optional
from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class KeycloakUser(BaseModel):
    """Represents an authenticated Keycloak user."""
    username: str
    email: Optional[str] = None
    roles: List[str] = []
    access_token: str


class TokenData(BaseModel):
    """Decoded JWT token payload fields used internally."""
    username: Optional[str] = None
    email: Optional[str] = None
    roles: List[str] = []


class LoginResponse(BaseModel):
    """Response returned after a successful login."""
    message: str
    username: str
    email: Optional[str] = None
    roles: List[str] = []
