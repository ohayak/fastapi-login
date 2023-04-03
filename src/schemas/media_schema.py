from typing import Any, Optional, Union
from uuid import UUID

from pydantic import validator

from middlewares.minio import get_ctx_client
from models.media_model import ImageMediaBase, MediaBase
from utils.partial import optional


class IMediaCreate(MediaBase):
    pass


# All these fields are optional
@optional
class IMediaUpdate(MediaBase):
    pass


class IMediaRead(MediaBase):
    id: Union[UUID, str]
    link: Optional[str] = None

    @validator(
        "link", pre=True, check_fields=False, always=True
    )  # Always true because link does not exist in the database
    def default_icon(cls, value: Any, values: Any) -> str:
        if values["path"] is None:
            return ""
        minio = get_ctx_client()
        url = minio.presigned_get_file(file_name=values["path"])
        return url


# Image Media
class IImageMediaCreate(ImageMediaBase):
    pass


# All these fields are optional
@optional
class IImageMediaUpdate(ImageMediaBase):
    pass


class IImageMediaRead(ImageMediaBase):
    media: Optional[IMediaRead]
