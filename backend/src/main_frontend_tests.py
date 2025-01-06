# login_register.py
import base64
import os
import random
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta
import os
import jwt

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

class Token(BaseModel):
    access_token: str
    token_type: str
    is_admin: bool

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

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
    }
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

def get_user(username: str) -> Optional[UserInDB]:
    """Fetch user data from the (fake) DB by username."""
    user_dict = fake_users_db.get(username)
    if user_dict:
        return UserInDB(**user_dict)
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with optional expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT token, returns the payload or None if invalid/expired."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

###############################################################################
# AUTHENTICATION FLOW
###############################################################################

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    1) Client sends username & password via form data.
    2) Verify user exists & password is correct.
    3) Return short-lived JWT if valid.
    """
    user_in_db = get_user(form_data.username)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password1",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password2",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user_in_db.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is disabled",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db.username},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer", "is_admin": True}

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    This function is used by protected endpoints.
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
    """
    Example protected endpoint.
    If the user isn't logged in (JWT invalid/expired), they'll get 401.
    """
    return {"username": current_user.username, "disabled": current_user.disabled}

# Update these based on what you need
origins = [
    "http://localhost:8501",  # Streamlit
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # or ["*"] for any origin (less secure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FramesRequest(BaseModel):
    frames: list[str]

@app.post("/upload_frames")
def upload_frames(data: FramesRequest):
    # data.frames is a list of base64-encoded PNG strings: "data:image/png;base64,iVBORw0KG..."
    num_frames = len(data.frames)
    save_dir = "captured_frames"
    os.makedirs(save_dir, exist_ok=True)
    # (Optional) do something with the frames, e.g. decode them:
    for idx, f in enumerate(data.frames):
        b64_str = f.split(",")[1]  # remove "data:image/png;base64,"
        img_bytes = base64.b64decode(b64_str)
        # Now you have the image bytes to e.g. save to disk, process, etc.
        with open(os.path.join(save_dir, f"frame_{idx}.png"), "wb") as img_file:
            img_file.write(img_bytes)
        # feed to model, store on disk, etc.

    # Return dummy inference
    prediction = random.choice(["cat", "dog", "bird", "car", "person"])
    return {"prediction": prediction, "frame_count": num_frames}
