"""Main module for fastapi backend application."""
from fastapi import FastAPI
from backend.src.db import init_db
from backend.src.routers.image_router import image_router
from backend.src.routers.recording_router import recording_router
from backend.src.routers.user_router import user_router
from backend.src.routers.translation_router import translation_router

app = FastAPI()
app.include_router(user_router, tags=["User"])
app.include_router(recording_router, tags=["Recording"])
app.include_router(image_router, tags=["Image"])


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Hello World"}


@app.on_event("startup")
async def startup_event() -> None:
    """Startup event to initialize the database."""
    await init_db()
