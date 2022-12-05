from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, Extra, validator
from pydantic.main import ModelMetaclass

try:
    import orjson as json
except ImportError:
    import json


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        extra = Extra.allow
        json_loads = json.loads
        json_dumps = json.dumps
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S"),
        }


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
