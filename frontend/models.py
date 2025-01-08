"""Models for the frontend service."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseSettings(BaseSettings):
    """Base settings."""

    # If environment variables do not exist, .env file is taken
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class FrontendSettings(BaseSettings):
    """Frontend settings model."""

    backend_server: str


class LoginRequest(BaseModel):
    """LoginRequest model for logging in a user."""

    username: str
    password: str
    grant_type: str = "password"
    scope: str = ""


class LoginResponse(BaseModel):
    """LoginResponse model for returning access token and admin status."""

    access_token: str
    is_admin: bool
    user_id: int


class UserRequest(BaseModel):
    """UserRequest model for creating a new user."""

    username: str
    email: str | None = None
    hashed_password: str | None = None
    is_admin: bool = False
    is_active: bool = True
    id: int | None = None
    username: str | None = None


class RegisterUserRequest(UserRequest):
    """RegisterUserRequest model for registering a new user."""

    password: str
    username: str
    email: str


frontend_settings = FrontendSettings()