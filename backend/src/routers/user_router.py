"""This module contains the user router for the FastAPI application."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.db import get_session
from src.models import User, UserCreate, UserRead, UserUpdate

user_router = APIRouter()


@user_router.post("/users/", response_model=UserRead)  # noqa: FAST001
def create_user(*, session: Annotated[Session, Depends(get_session)], user: UserCreate) -> UserRead:
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
    session.commit()
    session.refresh(user)
    return UserRead.model_validate(user)


@user_router.get("/users/{user_id}", response_model=UserRead)  # noqa: FAST001
def read_user(*, session: Annotated[Session, Depends(get_session)], user_id: int) -> UserRead:
    """Retrieve a user by their user ID.

    Args:
        session (Session): The database session dependency.
        user_id (int): The ID of the user to retrieve.

    Returns:
        UserRead: The user data in the UserRead response model.

    Raises:
        HTTPException: If the user with the specified ID is not found.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


@user_router.get("/users/", response_model=list[UserRead])  # noqa: FAST001
def read_users(*, session: Annotated[Session, Depends(get_session)]) -> list[UserRead]:
    """Retrieve a list of users.

    This endpoint retrieves all users from the database and returns them as a list
    of `UserRead` models.

    Parameters:
        session (Session): The database session dependency.

    Returns:
        list[UserRead]: A list of users in the `UserRead` model format.
    """
    users = session.exec(select(User)).all()
    return [UserRead.model_validate(user) for user in users]


@user_router.put("/users/{user_id}", response_model=UserRead)  # noqa: FAST001
def update_user(
    *, session: Annotated[Session, Depends(get_session)], user_id: int, user: UserUpdate
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
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username is not None:
        db_user.username = user.username
    if user.email is not None:
        db_user.email = user.email
    if user.password is not None:
        db_user.hashed_password = user.hashed_password
    if user.is_active is not None:
        db_user.is_active = user.is_active
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserRead.model_validate(db_user)


@user_router.delete("/users/{user_id}", response_model=UserRead)  # noqa: FAST001
def delete_user(*, session: Annotated[Session, Depends(get_session)], user_id: int) -> UserRead:
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
    session.delete(user)
    session.commit()
    return UserRead.model_validate(user)
