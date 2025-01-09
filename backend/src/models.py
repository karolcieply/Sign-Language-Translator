"""Pydantic models for the API request and response bodies."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendSettings(BaseSettings):
    """Backend settings model."""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

class TranslateRequest(BaseModel):
    """Pydantic model for the translation request body."""

    user_id: int
    frames: list[str]


class FeedbackRequest(BaseModel):
    """Pydantic model for the feedback request body."""

    recording_id: int
    feedback: int


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

backend_settings = BackendSettings()
