"""A service class to handle authentication-related operations."""

import os
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.db_models import User
from backend.src.models import backend_settings

SECRET_KEY = backend_settings.secret_key
ALGORITHM = backend_settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = backend_settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """A service class to handle authentication-related operations."""

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against the stored hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a plain-text password."""
        return pwd_context.hash(password)

    async def get_user(self, session: AsyncSession, username: str, email: str | None = None) -> User | None:
        """Fetch a user by username from the database."""
        result = await session.execute(select(User).where(or_(User.username == username, User.email == email)))
        user_record = result.scalars().first()
        if user_record:
            return user_record
        return None

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """Create a short-lived JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
