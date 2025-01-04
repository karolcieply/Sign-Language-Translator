from sqlmodel import SQLModel, Field, Relationship



class User(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    username: str
    email: str
    hashed_password: str
    is_active: bool = True

    recordings: list["Recording"] = Relationship(back_populates="user", cascade_delete=True)

class Recording(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")

    images: list["Image"] = Relationship(back_populates="recordings", cascade_delete=True)
    user: User = Relationship(back_populates="recordings")

class Image(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    image: bytes
    recording_id: int = Field(foreign_key="recording.id", ondelete="CASCADE")
    
    recording: Recording = Relationship(back_populates="images")