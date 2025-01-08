from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
class BaseSettings(BaseSettings):
    """Microlearning base settings."""

    # If environment variables do not exist, .env file is taken
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class FrontendSettings(BaseSettings):
    """Frontend settings model."""
    backend_server: str

class LoginRequest(BaseModel):
    username: str
    password: str
    grant_type: str = "password"
    scope: str = ""

class LoginResponse(BaseModel):
    access_token: str
    is_admin: bool
    user_id: int

class UserRequest(BaseModel):
    username: str
    email: str | None = None
    hashed_password: str | None = None
    is_admin: bool = False
    is_active: bool = True
    id: int | None = None
    username: str | None = None

class RegisterUserRequest(UserRequest):
    password: str
    username: str
    email: str

