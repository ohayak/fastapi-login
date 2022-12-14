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
    address: str = Field(max_length=255, nullable=True)
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
    lastname: str = Field(max_length=32, nullable=True)
    email: EmailStr
    phone: str = Field(max_length=15, nullable=True)
    fleet: Dict = Field(default={}, sa_column=Column(MutableDict.as_mutable(JSON)))
    job_id: int = Field(foreign_key="user_job.id", nullable=True)
    update_time: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": func.now(), "server_default": func.now()},
    )
    
    auth: User = Relationship(link_model=User)
    job: UserJob = Relationship(link_model=UserJob)
    company: Company = Relationship(link_model=Company)
    
    class Config:
        arbitrary_types_allowed = True

