from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, SecretStr, validator

from services.auth.models import User


class UserInfo(User):
    roles_: Optional[List[str]] = Field(alias="roles")
    groups_: Optional[List[str]] = Field(alias="groups")

    class Config:
        fields = {"password": {"exclude": True}}


class UserLoginOut(BaseModel):
    """User login information"""

    token_type: str = "bearer"
    access_token: str = None


class UserRegIn(BaseModel):
    """User registration information"""

    username: str = Field(max_length=32, unique=True, index=True, nullable=False)
    password: SecretStr = Field(max_length=128, nullable=False)
    email: EmailStr = Field(None, index=True, nullable=True)
    password2: str = Field(max_length=128)

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("password mismatch!")
        return v
