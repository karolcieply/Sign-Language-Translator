from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str
    grant_type: str = "password"
    scope: str = ""

class LoginResponse(BaseModel):
    access_token: str
    is_admin: bool

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str

class UpdateUserRequest(BaseModel):
    email: str
    is_admin: bool
    user_name: str

