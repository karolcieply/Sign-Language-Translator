from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from backend.src.config import DBSettings

engine = create_async_engine(DBSettings().database_url, echo=True)


async def get_session() -> AsyncSession:  # type: ignore  # noqa: PGH003
    """Get a new session."""
    session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)()  # type: ignore
    try:
        yield session
        await session.commit()
    finally:
        session.close()


async def init_db() -> None:
    """Initialize the database."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

