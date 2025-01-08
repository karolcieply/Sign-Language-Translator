from datetime import timedelta
from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.db import get_session
from backend.src.db_models import User
from backend.src.models import LoginResponse, RegisterRequest
from backend.src.services.auth_service import AuthService

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

auth_service = AuthService()


@auth_router.post("/login")
async def login(
    session: Annotated[AsyncSession, Depends(get_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> LoginResponse:
    """Log in a user and return an access token."""
    user = await auth_service.get_user(session, form_data.username)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Incorrect username or password")

    if not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Incorrect username or password")

    # Create short-lived access token
    access_token_expires = timedelta(minutes=15)  # or from config
    access_token = auth_service.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return LoginResponse(access_token=access_token, is_admin=user.is_admin, user_id=user.id)


@auth_router.post("/register")
async def register(session: Annotated[AsyncSession, Depends(get_session)], form_data: RegisterRequest) -> LoginResponse:
    """Register a new user and return an access token."""
    user = await auth_service.get_user(session, form_data.username, form_data.email)
    if user:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Username already registered")

    hashed_password = auth_service.get_password_hash(form_data.password)
    new_user = User(username=form_data.username, hashed_password=hashed_password, email=form_data.email)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Create short-lived access token
    access_token_expires = timedelta(minutes=15)
    access_token = auth_service.create_access_token(
        data={"sub": new_user.username},
        expires_delta=access_token_expires,
    )

    return LoginResponse(access_token=access_token, is_admin = new_user.is_admin, user_id = new_user.id)
