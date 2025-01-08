"""This module contains the image router for the FastAPI application."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.db import get_session
from backend.src.db_models import Image, Recording
from backend.src.models import FeedbackRequest, TranslateRequest
from backend.src.prediction import base64_to_ndarray

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
async def translate(data: TranslateRequest, session: Annotated[AsyncSession, Depends(get_session)]) -> dict:
    """Upload frames and return a prediction."""
    recording = await add_recording(data.user_id, session)
    await add_images(recording.id, data.frames, session)

    # perform prediction
    print("klatki", flush=True)
    print(base64_to_ndarray(data.frames), flush=True)

    return {"prediction": "tomek", "recording_id": recording.id}


@translation_router.post("/feedback")
async def feedback(data: FeedbackRequest, session: Annotated[AsyncSession, Depends(get_session)]) -> dict:
    """Save feedback for a recording."""
    recording = await session.get(Recording, data.recording_id)
    recording.feedback = data.feedback
    await session.commit()

    # save feedback

    return {"message": "Feedback saved."}
