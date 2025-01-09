"""Config module for the application."""

from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    """DBSettings is a configuration class for database settings.

    Attributes:
        POSTGRES_USER (str): The username for the PostgreSQL database.
        POSTGRES_PASSWORD (str): The password for the PostgreSQL database.
        POSTGRES_SERVER (str): The server address for the PostgreSQL database.
        POSTGRES_PORT (int): The port number for the PostgreSQL database.
        POSTGRES_DB (str): The name of the PostgreSQL database.
    """

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def database_url(self) -> str:
        """Returns the database URL."""
        return f"""postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"""
