from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from fastapi_pagination import Page
from pydantic.generics import GenericModel

DataType = TypeVar("DataType")
T = TypeVar("T")


class IResponse(GenericModel, Generic[T]):
    message: str = ""
    meta: Dict = {}
    data: Optional[T]


class IResponseList(GenericModel, Generic[T]):
    message: str = ""
    meta: Dict = {}
    data: Optional[List[T]]


class IResponsePage(GenericModel, Generic[T]):
    message: str = ""
    meta: Dict = {}
    data: Page[T]


def create_response(
    data: Optional[DataType],
    message: Optional[str] = "",
    meta: Optional[Union[Dict, Any]] = {},
) -> Dict[str, Any]:
    body_response = {"data": data, "message": message, "meta": meta}
    # It returns a dictionary to avoid double
    # validation https://github.com/tiangolo/fastapi/issues/3021
    return dict((k, v) for k, v in body_response.items() if v is not None)
