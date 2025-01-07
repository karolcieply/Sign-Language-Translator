"""This module defines the SQLModel models for the Sign Language Translator application."""

import datetime

from sqlmodel import Field, Relationship, SQLModel
from backend.src.utils import hash_password


class User(SQLModel, table=True):
    """Represents a user in the system.

    Attributes:
        id (int | None): The unique identifier for the user. Defaults to None.
        username (str): The username of the user.
        email (str): The email address of the user.
        hashed_password (str): The hashed password of the user.
        is_active (bool): Indicates whether the user is active. Defaults to True.
        is_admin (bool): Indicates whether the user is an admin. Defaults to False.
        recordings (list[Recording]): A list of recordings associated with the user.
                                      The relationship is bidirectional and supports cascade delete.
    """

    id: int | None = Field(primary_key=True, default=None)
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False

    recordings: list["Recording"] = Relationship(
        back_populates="user", cascade_delete=True
    )


class Recording(SQLModel, table=True):
    """Represents a recording of a sign language translation.

    Attributes:
        id (int | None): The unique identifier for the recording. Defaults to None.
        user_id (int): The ID of the user who created the recording. This is a foreign key referencing the user table.
        created_at (datetime.datetime): The timestamp when the recording was created. Defaults to the current datetime.
        prediction (str | None): The predicted translation of the recording. This should be changed to an ENUM in the future.
        feedback (float | None): The feedback score for the recording.
        images (list["Image"]): A list of images associated with the recording. This relationship has cascade delete enabled.
        user (User): The user who created the recording.
    """

    id: int | None = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    prediction: str | None = None  # change to ENUM
    feedback: float | None = None

    images: list["Image"] = Relationship(
        back_populates="recording", cascade_delete=True
    )
    user: User = Relationship(back_populates="recordings")


class Image(SQLModel, table=True):
    """Represents an image associated with a recording in the database.

    Attributes:
        id (int | None): The primary key of the image. Defaults to None.
        content (bytes): The binary content of the image.
        recording_id (int): The foreign key referencing the associated recording.
                            This field is set to cascade on delete.
        recording (Recording): The relationship to the Recording model,
                               back-populated by the "images" attribute.
    """

    id: int | None = Field(primary_key=True, default=None)
    content: bytes
    recording_id: int = Field(foreign_key="recording.id", ondelete="CASCADE")

    recording: Recording = Relationship(back_populates="images")


class UserCreate(SQLModel):
    """UserCreate is a data model for creating a new user.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The password for the user.
        is_admin (bool): Status indicating whether the user is an admin. Defaults to False.
    """

    username: str
    email: str
    password: str
    is_admin: bool = False

    @property
    def hashed_password(self) -> str:
        """Returns the hashed password."""
        return hash_password(self.password)


class UserRead(SQLModel):
    """UserRead model representing a user in the system.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Username of the user.
        email (str): Email address of the user.
        is_active (bool): Status indicating whether the user is active.
        is_admin (bool): Status indicating whether the user is an admin.
        hashed_password (str): Hashed password of the user.
    """

    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    hashed_password: str


class UserUpdate(SQLModel):
    """UserUpdate is a data model for updating an existing user.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The password for the user.
        is_active (bool): Status indicating whether the user is active.
        is_admin (bool): Status indicating whether the user is an admin.
    """

    username: str | None = None
    email: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None

    @property
    def hashed_password(self) -> str:
        """Returns the hashed password."""
        return hash_password(self.password)
