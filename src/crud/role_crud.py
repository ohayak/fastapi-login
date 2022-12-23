from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from db.asqlalchemy import db
from models.role_model import Role
from models.user_model import User
from schemas.role_schema import IRoleCreate, IRoleUpdate


class CRUDRole(CRUDBase[Role, IRoleCreate, IRoleUpdate]):
    async def get_role_by_name(self, *, name: str, db_session: Optional[AsyncSession] = None) -> Role:
        db_session = db_session or db.session
        role = await db_session.execute(select(Role).where(Role.name == name))
        return role.scalar_one_or_none()

    async def add_role_to_user(self, *, user: User, role_id: UUID) -> Role:
        role = await super().get(id=role_id)
        role.users.append(user)
        db.session.add(role)
        await db.session.commit()
        await db.session.refresh(role)
        return role


role = CRUDRole(Role)
