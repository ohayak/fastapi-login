import uuid
from collections import ChainMap
from inspect import isclass
from typing import Any, Container, Dict, Optional, Type, TypeVar, Union

from pydantic import BaseConfig, BaseModel, Field, create_model
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty


class _OrmConfig(BaseConfig):
    """Base config for Pydantic models."""

    orm_mode = True


Model = TypeVar("Model")


def _from_pydantic(model: Model) -> dict[Any, tuple[Any, Any]]:
    """Convert Pydantic dataclass to dict, for further including.

    :param model: Pydantic model dataclass
    :return: dict format model
    """
    fields, new_fields = model.__fields__, {}
    for name, value in fields.items():
        if hasattr(value, "type_"):
            if "__main__" in str(value.type_):
                new_fields[name] = Optional[_from_pydantic(value.type_)]
            else:
                new_fields[name] = (Optional[value.type_], ...)
    return new_fields


def _model_dict(model_name: str, dict_def: dict, *, inner: bool = False) -> Union[Model, dict[Any, tuple[Any, Any]]]:
    """Convert a dictionary to a form suitable for pydantic.create_model.

    :param model_name: Name of further schema
    :param dict_def: Source of fields data
    :param inner: If model field is nested
    :return: fields dict for pydantic.create_model
    """
    model_name = model_name.replace("_", " ").capitalize()
    fields = {}
    for name, value in dict_def.items():
        if isinstance(value, tuple):
            fields[name] = value
        elif isinstance(value, dict):
            fields[name] = (
                _model_dict(f"{model_name}_{name}", value, inner=True),
                ...,
            )
        else:
            raise ValueError(f"Field {model_name}:{value} has invalid syntax")
    return create_model(model_name, **fields) if inner else fields


def make_schema_from_orm(
    db_model: Type,
    *,
    model_name="",
    config: BaseConfig = _OrmConfig,
    include: tuple = (),
    exclude: Container[str] = (),
    exclude_all: Container[str] = (),
    required: Container[str] = (),
    validators: Dict[str, classmethod] = None,
) -> Model:
    """Convert SQLAlchemy model to Pydantic dataclass scheme.

    :param db_model: SQLAlchemy model class, not instance
    :param model_name: New model name. Structure: '{db_model} your_name'
    :param config: Pydantic Config class. By default – OrmConfig
    :param include: tuple of included elements, may be contain Pydantic
            model class or Dict[str: (type, field)]
    :param exclude: Exclude elements of tuple, by keys. Can't use this with
          exclude_all param
    :param exclude_all: Exclude all beside tuple, can't use this with
            'exclude' param
    :param required: Keys in this tuple will be marks 'required' in scheme
    :param validators: for example "key": (ValidatorClass, Field(...)).
            Validator Class should be contain __get_validators__ method.
    :return: Pydantic dataclass model
    """
    if exclude and exclude_all:
        raise ValueError("You can define only one of parameters(exclude, exclude_all)")

    inspection = inspect(db_model)
    fields, defaults = {}, {int: 0, float: 0.0, str: "", bool: False, dict: {}}
    for attr in inspection.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                if exclude_all and name not in exclude_all:
                    continue
                column, _type = attr.columns[0], None
                if str(column.type) == "UUID":
                    _type = uuid.UUID
                elif hasattr(column.type, "impl"):
                    if hasattr(column.type.impl, "python_type"):
                        _type = column.type.impl.python_type
                elif hasattr(column.type, "python_type"):
                    _type = column.type.python_type

                default = Field(defaults.get(_type, ...)) if name in required else defaults.get(_type, None)
                if column.default is None and not column.nullable:
                    default = ...
                fields[name] = (Optional[_type], default)
    fields = {k: v for (k, v) in fields.items() if not k.startswith("_")}

    if include:
        _includes = []
        for item in include:
            if isclass(item):
                if issubclass(item, BaseModel):
                    item = _from_pydantic(item)
            if not isinstance(item, dict):
                raise ValueError("Include incorrect type")
            item = _model_dict("include", item)
            _includes.append(item)
        include = ChainMap(*_includes)
        fields = {**fields, **include}
    new_model = create_model(
        f"{db_model.__name__} {model_name}",
        __config__=config,
        __validators__=validators,
        **fields,
    )
    return new_model
