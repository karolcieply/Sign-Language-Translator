from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """Get a new session."""
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """Initialize the database."""
    SQLModel.metadata.create_all(engine)
