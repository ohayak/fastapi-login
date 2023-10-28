from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel


class MediaBase(SQLModel):
    title: Optional[str]
    description: Optional[str]
    path: Optional[str]


class Media(BaseUUIDModel, MediaBase, table=True):
    pass


class ImageMediaBase(SQLModel):
    file_format: Optional[str]
    width: Optional[int]
    height: Optional[int]


class ImageMedia(BaseUUIDModel, ImageMediaBase, table=True):
    media_id: Optional[UUID] = Field(foreign_key="Media.id")
    media: Optional[Media] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
        }
    )
