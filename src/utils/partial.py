# https://github.com/pydantic/pydantic/issues/1223
# https://github.com/pydantic/pydantic/pull/3179
# Todo migrate to pydanticv2 partial
import inspect
from typing import Any

from pydantic import BaseModel
from pydantic.fields import ModelField


def optional(*fields):
    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.__fields__
        return dec(cls)
    return dec


def optionalany(*fields):
    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
            _cls.__fields__[field].type_ = Any
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.__fields__
        return dec(cls)
    return dec
