"""This module contains the image router for the FastAPI application."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.db import get_session
from backend.src.db_models import Image, Recording
from backend.src.models import TranslateRequest

translation_router = APIRouter()

async def add_recording(user_id: int, session: AsyncSession) -> Recording:
    """Add a recording to the database."""
    recording = Recording(user_id=user_id)
    session.add(recording)
    await session.commit()
    await session.refresh(recording)
    return recording


async def add_images(recording_id: int, images: list[str], session: AsyncSession) -> None:
    """Add images to database."""
    for img in images:
        session.add(Image(recording_id=recording_id, content=img))
    await session.commit()

@translation_router.post("/translate")
async def translate(data: TranslateRequest, session: Annotated[AsyncSession, Depends(get_session)]):
    """Upload frames and return a prediction."""
    recording = await add_recording(data.user_id, session)
    await add_images(recording.id, data.frames, session)

    # perform prediction

    return {"prediction": "tomek"}

@translation_router.post("/feedback")
async def feedback(data: dict, session: Annotated[AsyncSession, Depends(get_session)]):
    """Save feedback for a recording."""
    recording_id = data["recording_id"]
    feedback = data["feedback"]
    await session.execute(
        Recording.update().where(Recording.id == recording_id).values(feedback=feedback)
    )

    # save feedback

    return {"message": "Feedback saved."}

