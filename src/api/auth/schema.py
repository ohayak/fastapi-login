import string
from typing import Optional
from pydantic import EmailStr, Field, validator
from pydantic import BaseModel

class SearchReq(BaseModel):
    query: str = Field(max_length=80)


# class OrganizationPatchReq(metaclass=AllOptional):
#     pass


# class User(Base):
#     username: str
#     email: EmailStr | None = None
#     full_name: str | None = None
#     admin: bool | None = None


# class Token(BaseModel):
#     access_token: str
#     token_type: str


class Role(Base):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_admin = Column(Boolean(), default=False)
    owner_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("roles", back_populates="could")


class roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    create = Column(Boolean(), default=False)
    update = Column(Boolean(), default=False)
    delete = Column(Boolean(), default=False)


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    acces_token = Column(String, nullable=False)
    token_type = Column(String, nullable=False)
