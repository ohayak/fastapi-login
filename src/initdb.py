import asyncio
from typing import Dict, List, Union

from sqlmodel import text
from sqlmodel.ext.asyncio.session import AsyncSession, engine

import crud
from core.config import settings
from middlewares.asql import create_session
from schemas.group_schema import IGroupCreate
from schemas.role_schema import IRoleCreate
from schemas.user_schema import IUserCreate

roles: List[IRoleCreate] = [
    IRoleCreate(name="admin", description="Admin role"),
    IRoleCreate(name="user", description="User role"),
]

groups: List[IGroupCreate] = [IGroupCreate(name="administrators", description="This is the first group")]


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
        "group": "administrators",
    },
    {
        "data": IUserCreate(
            first_name="User",
            last_name="FastAPI",
            password="user",
            email="user@mycompany.com",
            is_superuser=False,
        ),
        "role": "user",
    },
]


async def initdb(db_session: AsyncSession) -> None:

    for role in roles:
        role_current = await crud.role.get_role_by_name(name=role.name, db_session=db_session)
        if not role_current:
            await crud.role.create(obj_in=role, db_session=db_session)

    for user in users:
        current_user = await crud.user.get_by_email(email=user["data"].email, db_session=db_session)
        role = await crud.role.get_role_by_name(name=user["role"], db_session=db_session)
        if not current_user:
            user["data"].role_id = role.id
            await crud.user.create_with_role(obj_in=user["data"], db_session=db_session)

    for group in groups:
        current_group = await crud.group.get_group_by_name(name=group.name, db_session=db_session)
        if not current_group:
            current_group = await crud.group.create(obj_in=group, db_session=db_session)
        current_users = []
        for user in users:
            if user.get("group") == current_group.name:
                current_users.append(await crud.user.get_by_email(email=user["data"].email, db_session=db_session))
        await crud.group.add_users_to_group(users=current_users, group_id=current_group.id, db_session=db_session)


async def main() -> None:
    print("Creating initial data")
    async with create_session(settings.ASYNC_DB_URL) as session:
        await initdb(session)
    print("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
