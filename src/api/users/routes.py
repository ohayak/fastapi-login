import contextlib

from fastapi import APIRouter, Depends, Form, Request, Response, Body, HTTPException
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
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


@router.post("/register", description="Registration", response_model=BaseApiOut[UserInfo])
@auth.requires(roles=['admin'])
async def register(request: Request, response: Response, payload: UserRegIn = Body(...),
                   db: AsyncSession = Depends(gen_auth_async_session)):
    try:
        new_user = User(username=payload.username,
                        password=CryptContext(schemes=["bcrypt"], deprecated="auto").hash(payload.password))
        user = UserInfo(**new_user.dict())
        db.add(payload)
        await db.flush()
        return BaseApiOut(data=user)
    except:
        raise HTTPException(status_code=409, detail="This email already registered")


# @router.get("/users", description="list_of_users", response_model=BaseApiOut[UserInfo])
@router.get("/users", description="list_of_users", response_model=list[UserInfo])
@auth.requires(roles=['admin'])
async def users_list(request: Request, response: Response, db: AsyncSession = Depends(gen_auth_async_session)):
    query = await db.execute(select(User).order_by(User.id))
    return query.scalars().all()


@router.delete("/users/{user_id}", description="delete_user_by_id", response_model=BaseApiOut[UserInfo])
@auth.requires(roles=['admin'])
async def remove_user(request: Request, response: Response, user_id: int, db=Depends(gen_auth_async_session)):
    try:
        query = db.execute(select(User).where(User.id == user_id))
        user = query.one()
        db.delete(user)
        return user
    except:
        raise HTTPException(status_code=409, detail="user not exist")


@router.patch("/users/{user_id}", description="update_user_by_id", response_model=BaseApiOut[UserInfo])
@auth.requires(roles=['admin'])
async def update_user_info(request: Request, response: Response, user_id: int, payload: UserRegIn = Body(...),
                           db=Depends(gen_auth_async_session)):
    query = db.execute(select(User).where(User.id == user_id))
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
    return query.scalars().all()


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
async def remove_groups(request: Request, response: Response, group_id :int, db=Depends(gen_auth_async_session)):
    try:
        query = db.execute(select(Role).where(Role.id == group_id))
        role = query.one()
        db.delete(role)
        db.commit()
        db.refresh(Group)
        return role
    except:
        HTTPException(status_code=407, detail=f"group with  id :{group_id} not exist")
