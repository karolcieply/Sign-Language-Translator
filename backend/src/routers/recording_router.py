"""This module contains the recording router for the FastAPI application."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.src.db import get_session
from backend.src.db_models import Recording

recording_router = APIRouter()


@recording_router.post("/recordings/")
async def create_recording(
    *, session: Annotated[AsyncSession, Depends(get_session)], recording: Recording,
) -> Recording:
    """Create a new recording.

    This endpoint allows the creation of a new recording by adding it to the database session,
    committing the session, and refreshing the recording instance.

    Args:
        session (Session): The database session dependency.
        recording (Recording): The recording instance to be created.

    Returns:
        Recording: The newly created recording instance.
    """
    session.add(recording)
    await session.commit()
    await session.refresh(recording)
    return recording


@recording_router.get("/recordings/{recording_id}")
async def read_recording(
    *, session: Annotated[AsyncSession, Depends(get_session)], recording_id: int,
) -> Recording:
    """Endpoint to retrieve a recording by its ID.

    Args:
        session (Session): The database session dependency.
        recording_id (int): The ID of the recording to retrieve.

    Returns:
        Recording: The recording object if found.

    Raises:
        HTTPException: If the recording is not found, raises a 404 HTTP exception.
    """
    recording = await session.get(Recording, recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording


@recording_router.get("/recordings/")
async def read_recordings(*, session: Annotated[AsyncSession, Depends(get_session)]) -> list[Recording]:
    """Endpoint to retrieve a list of recordings.

    This endpoint retrieves all recordings from the database using the provided session.

    Args:
        session (Session): The database session dependency.

    Returns:
        list[Recording]: A list of all recordings in the database.
    """
    recordings = await session.execute(select(Recording))
    return recordings.scalars().all()


@recording_router.put("/recordings/{recording_id}")
async def update_recording(
    *,
    session: Annotated[AsyncSession, Depends(get_session)],
    recording_id: int,
    recording: Recording,
) -> Recording:
    """Update an existing recording.

    This endpoint allows updating the details of an existing recording by its ID.

    Args:
        session (Session): The database session dependency.
        recording_id (int): The ID of the recording to update.
        recording (Recording): The recording data to update.

    Returns:
        Recording: The updated recording object.

    Raises:
        HTTPException: If the recording with the given ID is not found.
    """
    db_recording = await session.get(Recording, recording_id)
    if not db_recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    for key, value in recording.model_dump(exclude_unset=True).items():
        setattr(db_recording, key, value)
    session.add(db_recording)
    await session.commit()
    await session.refresh(db_recording)
    return db_recording


@recording_router.delete("/recordings/{recording_id}")
async def delete_recording(
    *, session: Annotated[AsyncSession, Depends(get_session)], recording_id: int,
) -> Recording:
    """Delete a recording by its ID.

    Args:
        session (Session): The database session dependency.
        recording_id (int): The ID of the recording to delete.

    Returns:
        Recording: The deleted recording object.

    Raises:
        HTTPException: If the recording with the given ID is not found.
    """
    recording = await session.get(Recording, recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    await session.delete(recording)
    await session.commit()
    return recording
