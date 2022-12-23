import logging
from io import BytesIO
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, Query, Response, UploadFile, status
from fastapi_pagination import Params
from sqlmodel import and_, select

import crud
from api import deps
from models import Role, User
from schemas.media_schema import IMediaCreate
from schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from schemas.role_schema import IRoleEnum
from schemas.user_schema import IUserCreate, IUserRead, IUserReadWithoutGroups, IUserStatus
from utils.exceptions import IdNotFoundException, NameNotFoundException, UserSelfDeleteException
from utils.minio_client import MinioClient
from utils.resize_image import modify_image

router = APIRouter()


@router.get("/list", response_model=IGetResponsePaginated[IUserReadWithoutGroups])
async def read_users_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])),
):
    """
    Retrieve users. Requires admin or manager role
    """
    logging.debug("start function")
    logging.debug(current_user)
    users = await crud.user.get_multi_paginated(params=params)
    return create_response(data=users)


@router.get(
    "/list/by_role_name",
    response_model=IGetResponsePaginated[IUserReadWithoutGroups],
)
async def read_users_list_by_role_name(
    user_status: Optional[IUserStatus] = Query(
        default=IUserStatus.active,
        description="User status, It is optional. Default is active",
    ),
    role_name: str = Query(default="", description="String compare with name or last name"),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Retrieve users by role name and status. Requires admin role
    """
    user_status = True if user_status == IUserStatus.active else False
    role = await crud.role.get_role_by_name(name=role_name)
    if not role:
        raise NameNotFoundException(Role, name=role_name)
    query = (
        select(User)
        .join(Role, User.role_id == Role.id)
        .where(and_(Role.name == role_name, User.is_active == user_status))
        .order_by(User.first_name)
    )
    users = await crud.user.get_multi_paginated(query=query, params=params)
    return create_response(data=users)


@router.get(
    "/order_by_created_at",
    response_model=IGetResponsePaginated[IUserReadWithoutGroups],
)
async def get_user_list_order_by_created_at(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])),
):
    """
    Gets a paginated list of users ordered by created datetime
    """
    users = await crud.user.get_multi_paginated_ordered(params=params, order_by="created_at")
    return create_response(data=users)


@router.get("/{user_id}", response_model=IGetResponseBase[IUserRead])
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])),
):
    """
    Gets a user by his/her id
    """
    if user := await crud.user.get(id=user_id):
        return create_response(data=user)
    else:
        raise IdNotFoundException(User, id=user_id)


@router.get("", response_model=IGetResponseBase[IUserRead])
async def get_my_data(
    current_user: User = Depends(deps.get_current_user()),
):
    """
    Gets my user profile information
    """
    return create_response(data=current_user)


@router.post("", response_model=IPostResponseBase[IUserRead], status_code=status.HTTP_201_CREATED)
async def create_user(
    new_user: IUserCreate = Depends(deps.user_exists),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Creates a new user
    """

    role = await crud.role.get(id=new_user.role_id)
    if not role:
        raise IdNotFoundException(Role, id=new_user.role_id)

    user = await crud.user.create_with_role(obj_in=new_user)
    return create_response(data=user)


@router.delete("/{user_id}", response_model=IDeleteResponseBase[IUserRead])
async def remove_user(
    user: User = Depends(deps.is_valid_user),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Deletes a user by his/her id
    """
    if current_user.id == user.id:
        raise UserSelfDeleteException()

    user = await crud.user.remove(id=user.id)
    return create_response(data=user)


# @router.post("/image", response_model=IPostResponseBase[IUserRead])
async def upload_my_image(
    title: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user()),
    minio_client: MinioClient = Depends(deps.minio_auth),
):
    """
    Uploads a user image
    """
    try:
        image_modified = modify_image(BytesIO(image_file.file.read()))
        data_file = minio_client.put_object(
            file_name=image_file.filename,
            file_data=BytesIO(image_modified.file_data),
            content_type=image_file.content_type,
        )
        media = IMediaCreate(title=title, description=description, path=data_file.file_name)
        user = await crud.user.update_photo(
            user=current_user,
            image=media,
            heigth=image_modified.height,
            width=image_modified.width,
            file_format=image_modified.file_format,
        )
        return create_response(data=user)
    except Exception as e:
        print(e)
        return Response("Internal server error", status_code=500)


# @router.post("/{user_id}/image", response_model=IPostResponseBase[IUserRead])
async def upload_user_image(
    user: User = Depends(deps.is_valid_user),
    title: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
    minio_client: MinioClient = Depends(deps.minio_auth),
):
    """
    Uploads a user image by his/her id
    """
    try:
        image_modified = modify_image(BytesIO(image_file.file.read()))
        data_file = minio_client.put_object(
            file_name=image_file.filename,
            file_data=BytesIO(image_modified.file_data),
            content_type=image_file.content_type,
        )
        media = IMediaCreate(title=title, description=description, path=data_file.file_name)
        user = await crud.user.update_photo(
            user=user,
            image=media,
            heigth=image_modified.height,
            width=image_modified.width,
            file_format=image_modified.file_format,
        )
        return create_response(data=user)
    except Exception as e:
        print(e)
        return Response("Internal server error", status_code=500)
