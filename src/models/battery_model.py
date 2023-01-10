from sqlalchemy import Column, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declared_attr

from core.config import settings

engine = create_engine(
    settings.ASYNC_DB_DATA_URI.replace("asyncpg", "psycopg2"),
)


class UUIDBase(object):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__

    __table_args__ = {"autoload_with": engine}

    id = Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
    )


Base = declarative_base(cls=UUIDBase)


class BatteryCompany(Base):
    ...


class BatteryMedia(Base):
    ...


class BatteryCell(Base):
    ...


class BatteryModel(Base):
    ...


class BatteryInfo(Base):
    ...


class CompanyData(Base):
    ...
