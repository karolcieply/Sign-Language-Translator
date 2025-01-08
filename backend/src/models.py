"""Pydantic models for the API request and response bodies."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseSettings(BaseSettings):
    """Microlearning base settings."""

    # If environment variables do not exist, .env file is taken
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class BackendSettings(BaseSettings):
    """Frontend settings model."""

    secret_key: str


class TranslateRequest(BaseModel):
    """Pydantic model for the translation request body."""

    user_id: int
    frames: list[str]


class LoginResponse(BaseModel):
    """Pydantic model for the login response body."""

    access_token: str
    is_admin: bool
    user_id: int


class RegisterRequest(BaseModel):
    """Pydantic model for the registration request body."""

    username: str
    email: str
    password: str
