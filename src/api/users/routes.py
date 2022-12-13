import contextlib

from fastapi import APIRouter, Depends, Form, Request, Response, Body
from fastapi.responses import RedirectResponse
from sqlmodel import select

from api.auth.schemas import UserRegIn
from crud.schema import BaseApiOut
from crud.utils import schema_create_by_schema
from services.auth import auth
from services.auth.models import User, Role, Group
from services.database import AsyncSession, gen_auth_async_session

router = APIRouter(prefix="/users")

router.dependencies.insert(0, Depends(auth.backend.authenticate))

UserInfo = schema_create_by_schema(auth.user_model, "UserInfo", exclude={"password"})


@router.post("/user", description="User Profile", response_model=BaseApiOut[UserInfo])
@auth.requires()
async def userinfo(request: Request):
    return BaseApiOut(data=request.user)


@router.post("/register", description="Registration", response_model=BaseApiOut[UserInfo])
@auth.requires(roles=['admin'])
async def register(request: Request, response: Response, payload: UserRegIn = Body(...),
                   db: AsyncSession = Depends(gen_auth_async_session)):
    print(payload)
    db.add(payload)
    db.commit()
    db.refresh()
    return BaseApiOut(data=payload)


# @router.get("/users", description="list_of_users", response_model=BaseApiOut[UserInfo])
@router.get("/users", description="list_of_users")
@auth.requires(roles=['admin'])
async def users_list(request: Request, response: Response, db: AsyncSession = Depends(gen_auth_async_session)):
    query = await db.execute(select(User).order_by(User.id))
    return query.scalars().all()


@router.delete("/users/{user_id}", description="delete_user_by_id")
# @router.delete("/users/{user_id}", description="delete_user_by_id", response_model=BaseApiOut[UserInfo])
@auth.requires(roles=['admin'])
async def remove_user(request: Request, response: Response, user_id, db=Depends(gen_auth_async_session)):
    query = db.execute(select(User).where(User.id == user_id))
    user = query.one()
    db.delete(user)
    return user


@router.patch("/users/{user_id}", description="update_user_by_id", response_model=BaseApiOut[UserInfo])
@auth.requires(roles=['admin'])
async def update_user_info(request: Request, response: Response, payload: UserRegIn = Body(...),
                           db=Depends(gen_auth_async_session)):
    pass


@router.post("/roles", description="create_role")
@auth.requires(roles=['admin'])
async def create_role(request: Request, response: Response, payload: Role = Body(...),
                      db=Depends(gen_auth_async_session)):
    new_role = Role(**payload.dict())
    print(new_role)
    db.add(new_role)
    db.commit()
    return {"message": "role added"}


@router.get("/roles", description="role_list")
@auth.requires(roles=['admin'])
async def get_roles(request: Request, response: Response, db: AsyncSession = Depends(gen_auth_async_session)):
    query = await db.execute(select(Role).order_by(Role.id))
    return query.scalars().all()


@router.delete("/roles/{id}", description="remove_role_by_id)", response_model=Role)
@auth.requires(roles=['admin'])
async def remove_role(request: Request, response: Response, user_id, db=Depends(gen_auth_async_session)):
    query = db.execute(select(Role).where(Role.id == user_id))
    role = query.one()
    db.delete(role)
    db.commit()
    return role


@router.post("/groups", description="create_group", response_model=Group)
@auth.requires(roles=['admin'])
async def create_group(request: Request, response: Response, payload: UserRegIn = Body(...),
                       db=Depends(gen_auth_async_session)):
    pass


@router.get("/groups", description="groups_list)", response_model=Group)
@auth.requires(roles=['admin'])
async def get_groups(request: Request, response: Response, db: AsyncSession =Depends(gen_auth_async_session)):
    query = await db.execute(select(Group).order_by(Group.id))
    return query.scalars().all()


@router.delete("/groups/{id}", description="remove_group_by_id)", response_model=Group)
@auth.requires(roles=['admin'])
async def remove_groups(request: Request, response: Response, user_id, db=Depends(gen_auth_async_session)):
    query = db.execute(select(Role).where(Role.id == user_id))
    role = query.one()
    db.delete(role)
    db.commit()
    return role
