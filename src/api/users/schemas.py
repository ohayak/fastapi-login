from typing import List, Optional, Dict

from pydantic import BaseModel, EmailStr, Field, SecretStr, validator

from services.auth.models import User
from api.auth.schemas import UserInfo, UserRegIn

class UserInfo(User):
    roles_: Optional[List[str]] = Field(alias="roles")
    groups_: Optional[List[str]] = Field(alias="groups")

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
