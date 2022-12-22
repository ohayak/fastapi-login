import contextlib
import logging

from fastapi import APIRouter, Depends, Form, Request, Response, Body, HTTPException
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlmodel import select

import api.auth.routes
from api.auth.schemas import UserRegIn, UserInfo
from api.users.schemas import NewUserForm
from crud.schema import BaseApiOut
from crud.utils import schema_create_by_schema
from models.entities import UserDetails
from services.auth import auth
from services.auth.models import User, Role, Group
from services.database import AsyncSession, gen_auth_async_session

router = APIRouter(prefix="/users")

router.dependencies.insert(0, Depends(auth.backend.authenticate))


@router.post("/user", response_model=BaseApiOut[UserDetails])
@auth.requires(roles=['admin'])
async def register(request: Request,
                   payload: NewUserForm,
                   db: AsyncSession = Depends(gen_auth_async_session)):
    print(payload)
    new_auth_user = api.auth.routes.register(request, payload, db)
    new_user = UserDetails(
        id=new_auth_user.id,
        email=payload.email,
        lastname=payload.lastname
    )
    db.add(new_user)
    return BaseApiOut(data=new_user)


@router.get("/users", description="list_of_users", response_model=list[UserDetails])
@auth.requires(roles=['admin'])
async def users_list(request: Request, response: Response, db: AsyncSession = Depends(gen_auth_async_session)):
    query = await db.execute(select(UserDetails).order_by(UserDetails.id))
    return query.scalars().all()


@router.get("/user/{user_id}", description="select_user_id", response_model=UserInfo)
@auth.requires(roles=['admin'])
async def user_info(request: Request, response: Response, user_id: int,
                    db: AsyncSession = Depends(gen_auth_async_session)):
    try:
        user = await db.get(User, user_id)
        roles = get_roles(request=request, response=response, db=db)
        logging.debug(roles)
        userinfo = UserInfo(id=user.id, username=user.username, create_time=user.create_time,
                            update_time=user.update_time, password=user.password, roles_rel=roles)
        return userinfo
    except:
        raise HTTPException(status_code=403, detail="user not exist")


@router.delete("/users/{user_id}", description="delete_user_by_id", response_model=BaseApiOut[UserDetails])
@auth.requires(roles=['admin'])
async def remove_user(request: Request, response: Response, user_id: int, db=Depends(gen_auth_async_session)):
    try:
        query = db.execute(select(UserDetails).where(UserDetails.id == user_id))
        user = query.one()
        db.delete(user)
        return user
    except:
        raise HTTPException(status_code=409, detail="user not exist")


@router.patch("/users/{user_id}", description="update_user_by_id", response_model=BaseApiOut[UserDetails])
@auth.requires(roles=['admin'])
async def update_user_info(request: Request, response: Response, user_id: int, payload: UserRegIn = Body(...),
                           db=Depends(gen_auth_async_session)):
    query = db.execute(select(UserDetails).where(UserDetails.id == user_id))
    user_current_data = query.one()
    new_data = payload.dict(exclude_unset=True)
    new_user_data = user_current_data.copy(update=new_data)
    try:
        db.add(new_user_data)
        db.commit()
        db.refresh(User)
        return new_user_data
    except:
        raise HTTPException(status_code=409, detail="This email already registered")


@router.post("/roles", description="create_role", response_model=Role)
@auth.requires(roles=['admin'])
async def create_role(request: Request, response: Response, payload: Role = Body(...),
                      db=Depends(gen_auth_async_session)):
    try:
        db.add(payload)
        db.commit()
        db.refresh(Role)
        return payload
    except:
        raise HTTPException(status_code=409, detail="role already exist")


@router.get("/roles", description="role_list")
@auth.requires(roles=['admin'])
async def get_roles(request: Request, response: Response, db: AsyncSession = Depends(gen_auth_async_session)):
    query = await db.execute(select(Role).order_by(Role.id))
    return list(query.scalars().all())


@router.delete("/roles/{role_id}", description="remove_role_by_id)", response_model=Role)
@auth.requires(roles=['admin'])
async def remove_role(request: Request, response: Response, role_id: int, db=Depends(gen_auth_async_session)):
    try:
        query = db.execute(select(Role).where(Role.id == role_id))
        role = query.one()
        db.delete(role)
        db.commit()
        db.refresh(Role)
        return role
    except:
        HTTPException(status_code=407, detail=f"group with  id :{role_id} not exist")


@router.post("/groups", description="create_group", response_model=Group)
@auth.requires(roles=['admin'])
async def create_group(request: Request, response: Response, payload: UserRegIn = Body(...),
                       db=Depends(gen_auth_async_session)):
    try:
        db.add(payload)
        db.commit()
        db.refresh(Group)
        return payload
    except:
        raise HTTPException(status_code=409, detail="group already exist")


@router.get("/groups", description="groups_list)", response_model=Group)
@auth.requires(roles=['admin'])
async def get_groups(request: Request, response: Response, db: AsyncSession = Depends(gen_auth_async_session)):
    query = await db.execute(select(Group).order_by(Group.id))
    return query.scalars().all()


@router.delete("/groups/{group_id}", description="remove_group_by_id)", response_model=Group)
@auth.requires(roles=['admin'])
async def remove_groups(request: Request, response: Response, group_id: int, db=Depends(gen_auth_async_session)):
    try:
        query = db.execute(select(Role).where(Role.id == group_id))
        group = query.one()
        db.delete(group)
        db.commit()
        db.refresh(Group)
        return group
    except:
        HTTPException(status_code=407, detail=f"group with  id :{group_id} not exist")
