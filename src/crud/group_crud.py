from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from db.asqlalchemy import db
from models.group_model import Group
from models.user_model import User
from schemas.group_schema import IGroupCreate, IGroupUpdate


class CRUDGroup(CRUDBase[Group, IGroupCreate, IGroupUpdate]):
    async def get_group_by_name(self, *, name: str, db_session: Optional[AsyncSession] = None) -> Group:
        db_session = db_session or db.session
        group = await db_session.execute(select(Group).where(Group.name == name))
        return group.scalar_one_or_none()

    async def add_user_to_group(self, *, user: User, group_id: UUID) -> Group:
        group = await super().get(id=group_id)
        group.users.append(user)
        db.session.add(group)
        await db.session.commit()
        await db.session.refresh(group)
        return group

    async def add_users_to_group(
        self,
        *,
        users: List[User],
        group_id: UUID,
        db_session: Optional[AsyncSession] = None,
    ) -> Group:
        db_session = db_session or db.session
        group = await super().get(id=group_id, db_session=db_session)
        group.users.extend(users)
        db_session.add(group)
        await db_session.commit()
        await db_session.refresh(group)
        return group


group = CRUDGroup(Group)
