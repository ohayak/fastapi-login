from io import BytesIO
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, Query, Response, UploadFile, status
from fastapi_pagination import Params
from sqlmodel import and_, select

import crud
from api.deps import get_current_user, is_valid_user, user_exists
from exceptions import ContentNoChangeException, IdNotFoundException, NameNotFoundException, UserSelfDeleteException
from middlewares import Minio, get_ctx_minio
from models import Role, User
from schemas.common_schema import FilterQuery
from schemas.media_schema import IMediaCreate
from schemas.response_schema import IResponse, IResponsePage, create_response
from schemas.role_schema import IRoleEnum
from schemas.user_schema import IUserCreate, IUserRead, IUserReadWithoutGroups, IUserStatus
from utils.resize_image import modify_image

router = APIRouter()


@router.get("/list", response_model=IResponsePage[IUserReadWithoutGroups])
async def list_users(
    filters: FilterQuery = Depends(),
    params: Params = Depends(),
    current_user: User = Depends(get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Retrieve users. Requires admin or manager role
    """
    users = await crud.user.get_multi_filtered_paginated(filters=filters, params=params)
    return create_response(data=users)


@router.get("/{user_id}", response_model=IResponse[IUserRead])
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Gets a user by id
    """
    if user := await crud.user.get(id=user_id):
        return create_response(data=user)
    else:
        raise IdNotFoundException(User, id=user_id)


@router.get("/me", response_model=IResponse[IUserRead])
async def get_my_data(
    current_user: User = Depends(get_current_user()),
):
    """
    Gets my user profile information
    """
    return create_response(data=current_user)


@router.post("/new", response_model=IResponse[IUserRead], status_code=status.HTTP_201_CREATED)
async def create_user(
    new_user: IUserCreate = Depends(user_exists),
    current_user: User = Depends(get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Creates a new user
    """

    role = await crud.role.get(id=new_user.role_id)
    if not role:
        raise IdNotFoundException(Role, id=new_user.role_id)

    user = await crud.user.create_with_role(obj_in=new_user)
    return create_response(data=user)


@router.delete("/{user_id}", response_model=IResponse[IUserRead])
async def delete_user(
    user: User = Depends(is_valid_user),
    current_user: User = Depends(get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Deletes a user by his/her id
    """
    if current_user.id == user.id:
        raise UserSelfDeleteException()

    user = await crud.user.delete(id=user.id)
    return create_response(data=user)


@router.post("/image", response_model=IResponse[IUserRead], include_in_schema=False)
async def upload_my_image(
    title: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user()),
    minio_client: Minio = Depends(get_ctx_minio),
):
    """
    Uploads a user image
    """
    try:
        image_modified = modify_image(BytesIO(image_file.file.read()))
        data_file = minio_client.upload_file(
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
        return Response(f"Internal server error {e}", status_code=500)


@router.post("/{user_id}/image", response_model=IResponse[IUserRead], include_in_schema=False)
async def upload_user_image(
    user: User = Depends(is_valid_user),
    title: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user(required_roles=[IRoleEnum.admin])),
    minio_client: Minio = Depends(get_ctx_minio),
):
    """
    Uploads a user image by his/her id
    """
    try:
        image_modified = modify_image(BytesIO(image_file.file.read()))
        data_file = minio_client.upload_file(
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
        return Response(f"Internal server error {e}", status_code=500)


@router.put("/{user_id}", response_model=IResponse[IUserRead])
async def update_user_info(
    user_id: UUID,
    user: IUserRead,
    current_user: User = Depends(get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Updates user informations
    """
    current_user_data = await crud.user.get(id=user_id)
    if not current_user_data:
        raise IdNotFoundException(User, id=user_id)

    if (
        current_user_data.first_name == user.first_name
        and current_user_data.last_name == user.last_name
        and current_user_data.email == user.email
        and current_user_data.is_superuser == user.is_superuser
        and current_user_data.phone == user.phone
        and current_user_data.role_id == user.role_id
    ):
        raise ContentNoChangeException()

    updated_user = await crud.user.update(obj_current=current_user_data, obj_new=user)
    return create_response(data=updated_user)
