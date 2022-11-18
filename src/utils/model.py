from typing import Any, Callable, Dict, Optional, Tuple

from pydantic import BaseModel as PydanticBaseModel
from pydantic.main import ModelMetaclass
from pydantic.utils import GetterDict


class SetterDict(GetterDict):
    def __setitem__(self, key: str, value: Any) -> Any:
        setattr(self._obj, key, value)


class BaseModel(PydanticBaseModel):
    def dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias: bool = False,
        exclude_unset: bool = True,
        exclude_defaults: bool = False,
        exclude_none: bool = True,
    ) -> Dict[str, Any]:
        return super().dict(
            by_alias=by_alias,
            include=include,
            exclude=exclude,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def json(
        self,
        *,
        include=None,
        exclude=None,
        by_alias: bool = False,
        exclude_unset: bool = True,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Optional[Callable[[Any], Any]] = None,
        **dumps_kwargs: Any,
    ) -> str:
        return super().json(
            by_alias=by_alias,
            include=include,
            exclude=exclude,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            **dumps_kwargs,
        )

    class Config:
        orm_mode = True
        # getter_dict = SetterDict


class AllOptional(ModelMetaclass):
    def __new__(self, name: str, bases: Tuple[type], namespaces: Dict[str, Any], **kwargs):
        annotations: dict = namespaces.get("__annotations__", {})

        for base in bases:
            for base_ in base.__mro__:
                if base_ is BaseModel:
                    break
                annotations.update(base_.__annotations__)

        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]

        namespaces["__annotations__"] = annotations

        return super().__new__(self, name, bases, namespaces, **kwargs)
