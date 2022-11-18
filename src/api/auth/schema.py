import string
from typing import Optional

from pydantic import EmailStr, Field, validator

from utils.model import AllOptional, BaseModel


class SearchReq(BaseModel):
    query: str = Field(max_length=80)

class OrganizationPatchReq(metaclass=AllOptional):
    pass
