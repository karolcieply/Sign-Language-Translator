from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.db import get_session
from src.models import Image

image_router = APIRouter()


@image_router.post("/images/", response_model=Image)
def create_image(*, session: Annotated[Session, Depends(get_session)], image: Image):
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


@image_router.get("/images/{image_id}", response_model=Image)
def read_image(*, session: Annotated[Session, Depends(get_session)], image_id: int):
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@image_router.get("/images/", response_model=list[Image])
def read_images(*, session: Annotated[Session, Depends(get_session)]):
    images = session.exec(select(Image)).all()
    return images


@image_router.put("/images/{image_id}", response_model=Image)
def update_image(
    *, session: Annotated[Session, Depends(get_session)], image_id: int, image: Image
):
    db_image = session.get(Image, image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    db_image.recording_id = image.recording_id
    db_image.url = image.url
    session.add(db_image)
    session.commit()
    session.refresh(db_image)
    return db_image


@image_router.delete("/images/{image_id}", response_model=Image)
def delete_image(*, session: Annotated[Session, Depends(get_session)], image_id: int):
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    session.delete(image)
    session.commit()
    return image
