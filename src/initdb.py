import asyncio
import csv
from typing import Dict, List, Union

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

import crud
from core.settings import settings
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
            last_name="",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email=settings.FIRST_SUPERUSER_EMAIL,
            is_superuser=True,
            is_verified=True,
        ),
        "role": "admin",
        "group": "administrators",
    },
    {
        "data": IUserCreate(
            first_name="User",
            last_name="One",
            password="P@ssUser1",
            email="user1@fast.api",
            is_superuser=False,
            is_verified=True,
        ),
        "role": "user",
    },
    {
        "data": IUserCreate(
            first_name="User",
            last_name="Two",
            password="P@ssUser2",
            email="user2@fast.api",
            is_superuser=False,
            is_verified=True,
        ),
        "role": "user",
    },
]


async def init_data_from_csv(db_session: AsyncSession, model, file_path: str):
    # Check if the table already has data
    existing_records = await db_session.execute(select(model))
    if existing_records.scalars().first():
        print(f"{model.__name__} table already initialized, skipping...")
        return

    # If the table is empty, proceed to insert data from the CSV file
    with open(file_path, "r") as file:
        csv_reader = csv.DictReader(file)
        print(f"{model.__name__} init table...")
        for row in csv_reader:
            current_obj = await db_session.execute(select(model).where(model.code == row["code"]))
            current_obj = current_obj.scalar_one_or_none()

            if not current_obj:
                if "languages" in row:
                    row["languages"] = row["languages"].split(";")
                if "countries" in row:
                    row["countries"] = row["countries"].split(";")
                obj = model(**row)
                db_session.add(obj)
                await db_session.commit()


async def initdb(db_session: AsyncSession) -> None:
    for role in roles:
        role_current = await crud.role.get_by_name(name=role.name, db_session=db_session)
        if not role_current:
            await crud.role.create(obj_in=role, db_session=db_session)

    for user in users:
        current_user = await crud.user.get_by_email(email=user["data"].email, db_session=db_session)
        role = await crud.role.get_by_name(name=user["role"], db_session=db_session)
        if not current_user:
            await crud.user.create_with_role(obj_in=user["data"], role_id=role.id, db_session=db_session)

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
