"""This module contains the user router for the FastAPI application."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.db import get_session
from src.models import User, UserCreate, UserRead, UserUpdate

user_router = APIRouter()


@user_router.post("/users/")
async def create_user(*, session: Annotated[AsyncSession, Depends(get_session)], user: UserCreate) -> UserRead:
    """Create a new user.

    This endpoint creates a new user in the database using the provided user data.
    The user data is validated and then added to the session. The session is committed
    to save the changes, and the user object is refreshed to reflect the saved state.

    Args:
        session (Session): The database session dependency.
        user (UserCreate): The user data to create a new user.

    Returns:
        UserRead: The created user data in the response model format.
    """
    user = User.model_validate(user)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


@user_router.get("/users/{user_id}")
async def read_user(*, session: Annotated[AsyncSession, Depends(get_session)], user_id: int) -> UserRead:
    """Retrieve a user by their user ID.

    Args:
        session (Session): The database session dependency.
        user_id (int): The ID of the user to retrieve.

    Returns:
        UserRead: The user data in the UserRead response model.

    Raises:
        HTTPException: If the user with the specified ID is not found.
    """
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


@user_router.get("/users/")
async def read_users(*, session: Annotated[AsyncSession, Depends(get_session)]) -> list[UserRead]:
    """Retrieve a list of users.

    This endpoint retrieves all users from the database and returns them as a list
    of `UserRead` models.

    Parameters:
        session (Session): The database session dependency.

    Returns:
        list[UserRead]: A list of users in the `UserRead` model format.
    """
    users = await session.execute(select(User))
    return [UserRead.model_validate(user) for user in users.scalars().all()]


@user_router.put("/users/{user_id}")
async def update_user(
    *, session: Annotated[AsyncSession, Depends(get_session)], user_id: int, user: UserUpdate
) -> UserRead:
    """Update an existing user.

    Args:
        session (Session): The database session dependency.
        user_id (int): The ID of the user to update.
        user (UserUpdate): The user update data.

    Raises:
        HTTPException: If the user with the given ID is not found.

    Returns:
        UserRead: The updated user data.
    """
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.model_dump(exclude_unset=True, exclude=["password"]).items():
        setattr(db_user, key, value)
    if user.password:
        db_user.hashed_password = user.hashed_password
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return UserRead.model_validate(db_user)


@user_router.delete("/users/{user_id}")
async def delete_user(*, session: Annotated[AsyncSession, Depends(get_session)], user_id: int) -> UserRead:
    """Delete a user by user ID.

    Args:
        session (Session): The database session dependency.
        user_id (int): The ID of the user to delete.

    Raises:
        HTTPException: If the user with the given ID is not found.

    Returns:
        UserRead: The deleted user's data.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(user)
    await session.commit()
    return UserRead.model_validate(user)
