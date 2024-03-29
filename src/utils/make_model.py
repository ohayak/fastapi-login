import uuid
from collections import ChainMap
from inspect import isclass
from typing import Any, Container, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, Field, create_model
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty
from sqlmodel import SQLModel

Model = TypeVar("Model", bound=SQLModel)
Schema = TypeVar("Schema", bound=BaseModel)


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


def _make_fields(
    db_model: Type,
    include: tuple = (),
    exclude: Container[str] = (),
    exclude_all: Container[str] = (),
    required: Container[str] = (),
):
    if exclude and exclude_all:
        raise ValueError("You can define only one of parameters(exclude, exclude_all)")

    fields, defaults = {}, {int: None, float: None, str: None, bool: None, dict: None}
    inspection = inspect(db_model)
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

    return fields


def make_schema_from_orm(
    *db_models: Type,
    model_name: str,
    include: tuple = (),
    exclude: Container[str] = (),
    exclude_all: Container[str] = (),
    required: Container[str] = (),
) -> Model:
    """Convert SQLAlchemy model to Pydantic dataclass scheme.

    :param db_models: SQLAlchemy model class, not instance. Order matters, if duplicated fields keep most right element
    :param model_name: New model name.
    :param include: tuple of included elements, may be contain Pydantic
            model class or Dict[str: (type, field)]
    :param exclude: Exclude elements of tuple, by keys. Can't use this with
          exclude_all param
    :param exclude_all: Exclude all beside tuple, can't use this with
            'exclude' param
    :param required: Keys in this tuple will be marks 'required' in scheme
    :return: Pydantic dataclass model
    """
    fields = {}
    for db_model in db_models:
        fields = fields | _make_fields(
            db_model,
            include,
            exclude,
            exclude_all,
            required,
        )
    new_model = create_model(
        model_name,
        __base__=SQLModel,
        __validators__=SQLModel.__validators__,
        **fields,
    )
    return new_model


def merge_schemas(
    schemas: Container[Model],
    schema_name: str = "",
    exclude: Container[str] = (),
) -> Model:
    fields = {}

    for model in schemas:
        for key, value in model.__fields__.items():
            if key not in exclude:
                fields[key] = (Optional[value.type_], value.default)

    return create_model(schema_name, **fields)


def map_models_schema(schema: Schema, models: List[Model]):
    return list(map(lambda model: schema.from_orm(model), models))
