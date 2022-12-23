from typing import Optional
from uuid import UUID

from sqlmodel import Field

from models.base_uuid_model import BaseUUIDModel


class LinkGroupUser(BaseUUIDModel, table=True):
    group_id: Optional[UUID] = Field(default=None, nullable=False, foreign_key="Group.id", primary_key=True)
    user_id: Optional[UUID] = Field(default=None, nullable=False, foreign_key="User.id", primary_key=True)
