from typing import List, Optional, Dict

from pydantic import BaseModel, EmailStr, Field, SecretStr, validator, root_validator

from services.auth.models import User
from api.auth.schemas import UserInfo, UserRegIn


class UserInfo(User):
    # roles: Optional[List[str]]
    # groups: Optional[List[str]]
    #
    # @root_validator
    # def set_value(cls, values):
    #     values["roles"] = values["roles_rel"]
    #     values["groups"] = values["groups_rel"]
    #     return values


    class Config:
        fields = {"password": {"exclude": True}}




class UserLoginOut(BaseModel):
    """User login information"""

    token_type: str = "bearer"
    access_token: str = None


class NewUserForm(UserRegIn):
    """User registration information"""
    email: EmailStr
    company_id: int
    firstname: str = Field(max_length=32)
    lastname: Optional[str] = Field(max_length=32)
    phone: Optional[str] = Field(max_length=15)
    fleet: Dict = Field(default={})
    job_id: Optional[int]
