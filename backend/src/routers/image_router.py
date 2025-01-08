"""This module contains the image router for the FastAPI application."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.src.db import get_session
from backend.src.db_models import Image

image_router = APIRouter()


@image_router.post("/images/")
async def create_image(*, session: Annotated[AsyncSession, Depends(get_session)], image: Image) -> Image:
    """Create a new image entry in the database.

    This endpoint allows for the creation of a new image entry in the database.
    It accepts an image object, adds it to the session, commits the transaction,
    and refreshes the image instance to reflect any changes made during the commit.

    Args:
        session (Session): The database session used for the transaction.
        image (Image): The image object to be added to the database.

    Returns:
        Image: The newly created image object with updated information from the database.
    """
    session.add(image)
    await session.commit()
    await session.refresh(image)
    return image


@image_router.get("/images/{image_id}")
async def read_image(*, session: Annotated[AsyncSession, Depends(get_session)], image_id: int) -> Image:
    """Retrieve an image by its ID.
    
    Args:
        session (Session): The database session dependency.
        image_id (int): The ID of the image to retrieve.
    
    Returns:
        Image: The image object if found.
    
    Raises:
        HTTPException: If the image is not found, raises a 404 HTTP exception.
    """
    image = await session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@image_router.get("/images/")
async def read_images(*, session: Annotated[AsyncSession, Depends(get_session)]) -> list[Image]:
    """Endpoint to retrieve a list of images.

    This endpoint retrieves all images from the database using the provided session.

    Args:
        session (Session): The database session dependency.

    Returns:
        list[Image]: A list of Image objects retrieved from the database.
    """
    images = await session.execute(select(Image))
    return images.scalars().all()


@image_router.put("/images/{image_id}")
async def update_image(
    *, session: Annotated[AsyncSession, Depends(get_session)], image_id: int, image: Image,
) -> Image:
    """Update an existing image.

    This endpoint updates the details of an existing image in the database.

    Args:
        session (Session): The database session dependency.
        image_id (int): The ID of the image to update.
        image (Image): The new image data to update.

    Returns:
        Image: The updated image object.

    Raises:
        HTTPException: If the image with the specified ID is not found.
    """
    db_image = await session.get(Image, image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    for key, value in image.model_dump(exclude_unset=True).items():
        setattr(db_image, key, value)
    session.add(db_image)
    await session.commit()
    await session.refresh(db_image)
    return db_image


@image_router.delete("/images/{image_id}")
async def delete_image(*, session: Annotated[AsyncSession, Depends(get_session)], image_id: int) -> Image:
    """Delete an image by its ID.

    Args:
        session (Session): The database session dependency.
        image_id (int): The ID of the image to delete.

    Returns:
        Image: The deleted image object.

    Raises:
        HTTPException: If the image with the given ID is not found.
    """
    image = await session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    await session.delete(image)
    await session.commit()
    return image
