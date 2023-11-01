from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Params

import crud
from exceptions import ContentNoChangeException, IdNotFoundException, NameExistException
from models.group_model import Group
from models.user_model import User
from schemas.group_schema import IGroupCreate, IGroupRead, IGroupUpdate
from schemas.response_schema import IResponse, IResponsePage, create_response

router = APIRouter()


@router.get("/list", response_model=IResponsePage[IGroupRead])
async def get_groups(
    params: Params = Depends(),
):
    """
    Gets a paginated list of groups
    """
    groups = await crud.group.get_multi_paginated(params=params)
    return create_response(data=groups)


@router.get("/{group_id}", response_model=IResponse[IGroupRead])
async def get_group_by_id(
    group_id: UUID,
):
    """
    Gets a group by its id
    """
    group = await crud.group.get(id=group_id)
    if group:
        return create_response(data=group)
    else:
        raise IdNotFoundException(Group, group_id)


@router.post(
    "/new",
    response_model=IResponse[IGroupRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_group(
    group: IGroupCreate,
):
    """
    Creates a new group
    """
    group_current = await crud.group.get_group_by_name(name=group.name)
    if group_current:
        raise NameExistException(Group, name=group.name)
    new_group = await crud.group.create(obj_in=group)
    return create_response(data=new_group)


@router.put("/{group_id}", response_model=IResponse[IGroupRead])
async def update_group(
    group_id: UUID,
    group: IGroupUpdate,
):
    """
    Updates a group by its id
    """
    group_current = await crud.group.get(id=group_id)
    if not group_current:
        raise IdNotFoundException(Group, group_id=group_id)

    if group_current.name == group.name and group_current.description == group.description:
        raise ContentNoChangeException()

    group_updated = await crud.group.update(obj_current=group_current, obj_new=group)
    return create_response(data=group_updated)


@router.delete("/{group_id}", response_model=IResponse[IGroupRead])
async def delete_group(
    group_id: UUID,
):
    """
    Deletes a group by id
    """
    group = await crud.group.get(id=group_id)
    if not group:
        raise IdNotFoundException(Group, group_id)
    group = await crud.group.delete(id=group_id)
    return create_response(data=group)


@router.post("/{group_id}/add_user/{user_id}", response_model=IResponse[IGroupRead])
async def add_user_into_a_group(
    user_id: UUID,
    group_id: UUID,
):
    """
    Adds a user into a group
    """
    user = await crud.user.get(id=user_id)
    if not user:
        raise IdNotFoundException(User, id=user_id)

    group = await crud.group.get(id=group_id)
    if not group:
        raise IdNotFoundException(Group, group_id)

    group = await crud.group.add_user_to_group(user=user, group_id=group_id)
    return create_response(message="User added to group", data=group)


@router.post("/{group_id}/delete_user/{user_id}", response_model=IResponse[IGroupRead])
async def delete_user_from_group(
    user_id: UUID,
    group_id: UUID,
):
    """
    remove a user from a group
    """
    user = await crud.user.get(id=user_id)
    if not user:
        raise IdNotFoundException(User, id=user_id)

    group = await crud.group.get(id=group_id)
    if not group:
        raise IdNotFoundException(Group, group_id)

    group = await crud.group.delete_user_from_group(user=user, group_id=group_id)
    return create_response(message="User removed from group", data=group)
