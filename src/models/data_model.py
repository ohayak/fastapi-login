from typing import List

from sqlmodel import ARRAY, VARCHAR, Column, Field

from models.base_uuid_model import SQLModel


class Country(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: str
    languages: List[str] = Field(sa_column=Column(ARRAY(VARCHAR())))
    flag: str
