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
    IRoleCreate(name="senator", description="Player role"),
    IRoleCreate(name="deputy", description="Player role"),
    IRoleCreate(name="citizen", description="Player role"),
]

groups: List[IGroupCreate] = [
    IGroupCreate(name="admin", description="Administrators"),
    IGroupCreate(name="player", description="Human Players"),
    IGroupCreate(name="gm", description="Game Masters"),
    IGroupCreate(name="npc", description="non-player character"),
    IGroupCreate(name="bot", description="non-human character"),
]


users: List[Dict[str, Union[str, IUserCreate]]] = [
    {
        "data": IUserCreate(
            first_name="Admin",
            last_name="",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email=settings.FIRST_SUPERUSER_EMAIL,
            is_superuser=True,
            email_verified=True,
        ),
        "group": "admin",
        "role": None,
    },
    {
        "data": IUserCreate(
            first_name="User",
            last_name="One",
            password="P@ssUser1",
            email="user1@fast.api",
            is_superuser=False,
            email_verified=True,
        ),
        "group": "player",
        "role": "citizen",
    },
    {
        "data": IUserCreate(
            first_name="User",
            last_name="Two",
            password="P@ssUser2",
            email="user2@fast.api",
            is_superuser=False,
            email_verified=True,
        ),
        "group": "player",
        "role": "citizen",
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


async def initdb() -> None:
    db_session = create_session(settings.ASYNC_DB_URL)
    try:
        for role in roles:
            role_current = await crud.role.get_by("name", role.name, db_session=db_session)
            if not role_current:
                await crud.role.create(obj_in=role, db_session=db_session)

        for user in users:
            current_user = await crud.user.get_by("email", user["data"].email, db_session=db_session)
            if not current_user:
                current_user = await crud.user.create(obj_in=user["data"], db_session=db_session)
            if role := await crud.role.get_by("name", user["role"], db_session=db_session):
                await crud.user.update(obj_current=current_user, obj_new={"role_id": role.id}, db_session=db_session)

        for group in groups:
            current_group = await crud.group.get_by("name", group.name, db_session=db_session)
            if not current_group:
                current_group = await crud.group.create(obj_in=group, db_session=db_session)
            for user in users:
                if user.get("group") == current_group.name:
                    user_obj = await crud.user.get_by("email", user["data"].email, db_session=db_session)
                    await crud.user.add_to_group(user_obj, group_id=current_group.id, db_session=db_session)
            await db_session.commit()
    except Exception as e:
        await db_session.rollback()
        raise e
    finally:
        await db_session.close()


async def main():
    print("Creating initial data")
    await initdb()
    print("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
