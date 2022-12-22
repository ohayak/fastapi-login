from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Union

from pydantic import BaseModel, SecretStr, EmailStr
from sqlalchemy import and_, func, Column
from sqlalchemy.sql.selectable import Exists
from sqlmodel import Field, Relationship, Session, SQLModel, select
from sqlalchemy.ext.mutable import Mutable, MutableDict
from sqlalchemy.types import JSON
from services.auth.models import User


class UserJob(SQLModel, table=True):
    __tablename__ = "user_job"
    id: int = Field(primary_key=True)
    name: str = Field(max_length=32)


class Company(SQLModel, table=True):
    __tablename__ = "company"
    id: int = Field(primary_key=True)
    name: str = Field(max_length=32)
    address: Optional[str] = Field(max_length=255)
    contact_id: int = Field(foreign_key="auth_user.id")
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": func.now(), "server_default": func.now()},
    )


class UserDetails(SQLModel, table=True):
    __tablename__ = "user"
    id: int = Field(primary_key=True, foreign_key="auth_user.id")
    company_id: int = Field(foreign_key="company.id")
    firstname: str = Field(max_length=32)
    lastname: str = Field(max_length=32)
    email: EmailStr
    phone: Optional[str] = Field(max_length=15)
    fleet: Optional[Dict] = Field(default={}, sa_column=Column(MutableDict.as_mutable(JSON)))
    job_id: Optional[int] = Field(foreign_key="user_job.id")
    update_time: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": func.now(), "server_default": func.now()},
    )

    auth: User = Relationship()
    job: UserJob = Relationship()
    company: Company = Relationship()

    class Config:
        arbitrary_types_allowed = True
