from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from db.asqlalchemy import db
from models.company_model import Company
from models.user_model import User
from schemas.company_schema import ICompanyCreate, ICompanyUpdate


class CRUDCompany(CRUDBase[Company, ICompanyCreate, ICompanyUpdate]):
    async def get_company_by_name(self, *, name: str, db_session: Optional[AsyncSession] = None) -> Company:
        db_session = db_session or db.session
        company = await db_session.execute(select(Company).where(Company.name == name))
        return company.scalar_one_or_none()

    async def add_user_to_company(self, *, user: User, company_id: UUID) -> Company:
        company = await super().get(id=company_id)
        company.users.append(user)
        db.session.add(company)
        await db.session.commit()
        await db.session.refresh(company)
        return company

    async def add_users_to_company(
        self,
        *,
        users: List[User],
        company_id: UUID,
        db_session: Optional[AsyncSession] = None,
    ) -> Company:
        db_session = db_session or db.session
        company = await super().get(id=company_id, db_session=db_session)
        company.users.extend(users)
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)
        return company

    async def add_contact_to_company(
        self, *, user: User, company_id: UUID, db_session: Optional[AsyncSession] = None
    ) -> Company:
        db_session = db_session or db.session
        company = await super().get(id=company_id)
        company.contact = user
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)
        return company

    async def remove_user(
        self, *, user: User, company_id: UUID, db_session: Optional[AsyncSession] = None
    ) -> Company:
        db_session = db_session or db.session
        company = await super().get(id=company_id)
        company.users.remove(user)
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)
        return company

company = CRUDCompany(Company)
