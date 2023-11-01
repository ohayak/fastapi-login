from enum import Enum
from uuid import UUID

from sqlmodel import VARCHAR, Column, Field, Relationship, UniqueConstraint

from models.base_uuid_model import BaseUUIDModel, SQLModel
from models.user_model import User


class SocialAccountProviderEnum(str, Enum):
    twitter = "twitter"
    discord = "discord"


class SocialAccountBase(SQLModel):
    provider: SocialAccountProviderEnum = Field(sa_column=Column(VARCHAR, nullable=False))
    user_id: UUID = Field(foreign_key="User.id")
    username: str
    account_id: str
    is_verified: bool = Field(default=True)


class SocialAccount(BaseUUIDModel, SocialAccountBase, table=True):
    __table_args__ = (UniqueConstraint("user_id", "provider"),)
    user: User = Relationship(sa_relationship_kwargs={"lazy": "selectin"})  # noqa: F821


# class SocialEngagementBase(SQLModel):
#     content_id: str  # ID of the content on which the engagement was made
#     reaction_type: str  # Reaction type (e.g., like, retweet, comment)
#     reaction_date: datetime
#     socialaccount_media_id: UUID = Field(foreign_key="SocialMedia.id")  # noqa: F821


# class SocialEngagement(BaseUUIDModel, SocialEngagementBase, table=True):
#     socialaccount_media: SocialMedia = Relationship(
#         back_populates="engagements", sa_relationship_kwargs={"lazy": "selectin"}
#     )  # noqa: F821
