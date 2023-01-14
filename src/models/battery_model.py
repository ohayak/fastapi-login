from enum import Enum

from sqlalchemy import VARCHAR, Column
from sqlalchemy import Enum as saEnum
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declared_attr

from core.config import settings

engine = create_engine(
    settings.DB_DATA_URI,
)


class _Base(object):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__

    __table_args__ = {"autoload_with": engine}


class _UUIDBase(_Base):
    id = Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
    )


Base = declarative_base(cls=_Base)
UUIDBase = declarative_base(cls=_UUIDBase)


class BatteryStateEnum(str, Enum):
    USE = "USE"
    TO_REPAIR = "TO_REPAIR"
    REPAIRING = "REPAIRING"
    STORED = "STORED"
    TRANSPORT = "TRANSPORT"


class BatteryIncidentEnum(str, Enum):
    BROKEN_CONNECTOR = "BROKEN_CONNECTOR"
    NOT_CHARGING = "NOT_CHARGING"
    BMS_ERROR = "BMS_ERROR"
    WATER_DAMAGE = "WATER_DAMAGE"
    DEAD_BATTERY = "DEAD_BATTERY"


class BatteryStatusEnum(str, Enum):
    VERY_GOOD = "VERY_GOOD"
    GOOD = "GOOD"
    BAD = "BAD"
    CRITICAL = "CRITICAL"


class BatteryCompany(UUIDBase):
    ...


class BatteryMedia(UUIDBase):
    ...


class BatteryCell(UUIDBase):
    ...


class BatteryModel(UUIDBase):
    ...


class BatteryInfo(Base):
    ...


class CompanyData(Base):
    ...


class BatteryReview(UUIDBase):
    ...


class BatteryState(UUIDBase):
    state = Column(saEnum(BatteryStateEnum))
    incident = Column(saEnum(BatteryIncidentEnum))


class BatteryEvolution(UUIDBase):
    status = Column(saEnum(BatteryStatusEnum))
