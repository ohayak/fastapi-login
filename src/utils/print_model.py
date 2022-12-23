from typing import TypeVar

from fastapi.encoders import jsonable_encoder
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


def print_model(text: str = "", model: ModelType = None):
    """
    It prints sqlmodel responses for complex relationship models.
    """
    return print(text, jsonable_encoder(model))
