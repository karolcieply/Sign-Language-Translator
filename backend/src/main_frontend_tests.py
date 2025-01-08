# login_register.py
import os
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

###############################################################################
# SETTINGS & CONFIG
###############################################################################

# IMPORTANT: In production, load this from environment or a secure secret manager
SECRET_KEY = os.environ.get("SECRET_KEY", "dsakjfhdsakljfhdsakjhiuqaehwjkhksadjfhkldasjhnjk")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # short-lived access token (e.g. 30 minutes)

app = FastAPI()

# Setup a password context for hashing (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme (fastapi will look for Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

###############################################################################
# MODELS
###############################################################################



###############################################################################
# FAKE DATABASE (EXAMPLE ONLY)
###############################################################################

# This is just a dict for demonstration. Replace with a real database table.
# The password "wonderland" is bcrypt-hashed.
# (You can generate your own with: passlib.context.CryptContext(schemes=["bcrypt"]).hash("wonderland"))
fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": "$2b$12$Z1U2vwD67ra2IomKXJS7Q.efcJzeYJErHJYvaXt4tgLKgNyUljj0C",  # "wonderland"
        "disabled": False,
    },
}

###############################################################################
# UTILITY FUNCTIONS
###############################################################################

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against the stored hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a plain-text password (for creating new users)."""
    return pwd_context.hash(password)

def get_user(username: str) -> UserInDB | None:
    """Fetch user data from the (fake) DB by username."""
    user_dict = fake_users_db.get(username)
    if user_dict:
        return UserInDB(**user_dict)
    return None

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT token with optional expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    """Decode a JWT token, returns the payload or None if invalid/expired."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

###############################################################################
# AUTHENTICATION FLOW
###############################################################################



def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """This function is used by protected endpoints.
    1) Extract token from "Authorization: Bearer <token>".
    2) Decode & validate the token.
    3) Fetch the user from DB.
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is disabled",
        )

    return user

@app.get("/users/me")
def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """Example protected endpoint.
    If the user isn't logged in (JWT invalid/expired), they'll get 401.
    """
    return {"username": current_user.username, "disabled": current_user.disabled}
