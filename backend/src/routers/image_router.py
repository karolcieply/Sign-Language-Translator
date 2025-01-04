"""This module contains the image router for the FastAPI application."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.db import get_session
from src.models import Image

image_router = APIRouter()


@image_router.post("/images/", response_model=Image)  # noqa: FAST001
def create_image(*, session: Annotated[Session, Depends(get_session)], image: Image) -> Image:
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
    session.commit()
    session.refresh(image)
    return image


@image_router.get("/images/{image_id}", response_model=Image)  # noqa: FAST001
def read_image(*, session: Annotated[Session, Depends(get_session)], image_id: int) -> Image:
    """Retrieve an image by its ID.
    
    Args:
        session (Session): The database session dependency.
        image_id (int): The ID of the image to retrieve.
    
    Returns:
        Image: The image object if found.
    
    Raises:
        HTTPException: If the image is not found, raises a 404 HTTP exception.
    """
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@image_router.get("/images/", response_model=list[Image])  # noqa: FAST001
def read_images(*, session: Annotated[Session, Depends(get_session)]) -> list[Image]:
    """Endpoint to retrieve a list of images.

    This endpoint retrieves all images from the database using the provided session.

    Args:
        session (Session): The database session dependency.

    Returns:
        list[Image]: A list of Image objects retrieved from the database.
    """
    images = session.exec(select(Image)).all()
    return images


@image_router.put("/images/{image_id}", response_model=Image)  # noqa: FAST001
def update_image(
    *, session: Annotated[Session, Depends(get_session)], image_id: int, image: Image
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
    db_image = session.get(Image, image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    db_image.recording_id = image.recording_id
    db_image.url = image.url
    session.add(db_image)
    session.commit()
    session.refresh(db_image)
    return db_image


@image_router.delete("/images/{image_id}", response_model=Image)  # noqa: FAST001
def delete_image(*, session: Annotated[Session, Depends(get_session)], image_id: int) -> Image:
    """Delete an image by its ID.

    Args:
        session (Session): The database session dependency.
        image_id (int): The ID of the image to delete.

    Returns:
        Image: The deleted image object.

    Raises:
        HTTPException: If the image with the given ID is not found.
    """
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    session.delete(image)
    session.commit()
    return image
