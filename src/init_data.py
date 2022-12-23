import asyncio
import logging
from db.session import SessionLocal


import crud
from typing import Dict, List, Union
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas.role_schema import IRoleCreate
from core.config import settings
from schemas.user_schema import IUserCreate, IUserRead
from schemas.group_schema import IGroupCreate

roles: List[IRoleCreate] = [
    IRoleCreate(name="admin", description="Admin role"),
    IRoleCreate(name="manager", description="Manager role"),
    IRoleCreate(name="operator", description="Operator role"),
]

groups: List[IGroupCreate] = [
    IGroupCreate(name="GR1", description="This is the first group")
]

users: List[Dict[str, Union[str, IUserCreate]]] = [
    {
        "data": IUserCreate(
            first_name="Admin",
            last_name="FastAPI",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email=settings.FIRST_SUPERUSER_EMAIL,
            is_superuser=True,
        ),
        "role": "admin",
    },
    {
        "data": IUserCreate(
            first_name="Manager",
            last_name="FastAPI",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email="manager@example.com",
            is_superuser=False,
        ),
        "role": "manager",
    },
    {
        "data": IUserCreate(
            first_name="Operator",
            last_name="FastAPI",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email="operator@example.com",
            is_superuser=False,
        ),
        "role": "operator",
    },
]


async def init_db(db_session: AsyncSession) -> None:

    for role in roles:
        role_current = await crud.role.get_role_by_name(
            name=role.name, db_session=db_session
        )
        if not role_current:
            await crud.role.create(obj_in=role, db_session=db_session)

    for user in users:
        current_user = await crud.user.get_by_email(
            email=user["data"].email, db_session=db_session
        )
        role = await crud.role.get_role_by_name(
            name=user["role"], db_session=db_session
        )
        if not current_user:
            user["data"].role_id = role.id
            await crud.user.create_with_role(obj_in=user["data"], db_session=db_session)

    for group in groups:
        current_group = await crud.group.get_group_by_name(
            name=group.name, db_session=db_session
        )
        if not current_group:
            new_group = await crud.group.create(obj_in=group, db_session=db_session)
            current_users = []
            for user in users:
                current_users.append(
                    await crud.user.get_by_email(
                        email=user["data"].email, db_session=db_session
                    )
                )
            await crud.group.add_users_to_group(
                users=current_users, group_id=new_group.id, db_session=db_session
            )


async def create_init_data() -> None:
    async with SessionLocal() as session:
        await init_db(session)


async def main() -> None:
    logging.info("Creating initial data")
    await create_init_data()
    logging.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
