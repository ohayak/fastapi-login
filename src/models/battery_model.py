#############################
# Models Copy from API WORKER
#############################

from datetime import datetime
from enum import Enum, auto
from typing import List, Optional

from sqlmodel import ARRAY, VARCHAR, Column, Field, ForeignKey, Integer, Relationship, and_, func
from sqlmodel.sql.sqltypes import GUID

from models.base_uuid_model import UUID, BaseUUIDModel, SQLModel


class BatteryCompany(BaseUUIDModel):
    name: str = Field(unique=True)


class Media(BaseUUIDModel):
    title: Optional[str]
    description: Optional[str]
    path: Optional[str]
    category: Optional[str]
    confidentiality: Optional[str]
    kind: Optional[str]
    size_kb: Optional[int]


class LinkBatteryModelMedia(SQLModel):
    media_id: Optional[UUID] = Field(
        sa_column=Column(GUID, ForeignKey("Media.id", ondelete="cascade"), primary_key=True)
    )
    model_id: Optional[UUID] = Field(
        sa_column=Column(GUID, ForeignKey("BatteryModel.id", ondelete="set null"), primary_key=True)
    )


class BatteryModel(BaseUUIDModel):
    name: str = Field(unique=True)
    manufacturer: Optional[str]
    value: Optional[int]
    nominal_capacity: Optional[float]
    voltage: Optional[int]
    number_cells: Optional[int]
    xsyp: Optional[str]
    weight: Optional[float]
    length: Optional[int]
    height: Optional[int]
    width: Optional[int]
    cells_model: Optional[str]
    siliconned: Optional[bool]
    charger: Optional[bool]
    communicaing: Optional[bool]
    locked: Optional[bool]
    diag_tool: Optional[bool]
    msds_url: Optional[str]
    un38_3: Optional[str]

    medias: Optional[List[Media]] = Relationship(
        link_model=LinkBatteryModelMedia,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class LinkBatteryCellMedia(SQLModel):
    media_id: Optional[UUID] = Field(
        sa_column=Column(GUID, ForeignKey("Media.id", ondelete="cascade"), primary_key=True)
    )
    cell_id: Optional[UUID] = Field(
        sa_column=Column(GUID, ForeignKey("BatteryCell.id", ondelete="set null"), primary_key=True)
    )


class BatteryCell(BaseUUIDModel):
    name: str = Field(unique=True)
    nominal_capacity: Optional[float]
    cells_ref: Optional[str]
    chemistry: Optional[str]
    color: Optional[str]
    nominal_capacity: Optional[float]
    voltage: Optional[float]
    form_factor: Optional[str]
    weight: Optional[float]
    energy_density: Optional[float]
    max_voltage: Optional[float]
    min_voltage: Optional[float]
    discharge_rate: Optional[float]
    max_discharge: Optional[float]
    other_names: Optional[List[str]] = Field(sa_column=Column(ARRAY(VARCHAR)))

    medias: Optional[List[Media]] = Relationship(
        link_model=LinkBatteryCellMedia,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class BatteryInfo(BaseUUIDModel):
    name: Optional[str] = Field(unique=True)
    external_id: Optional[str]
    model_id: Optional[UUID] = Field(sa_column=Column(GUID, ForeignKey("BatteryModel.id", ondelete="set null")))
    company_id: Optional[UUID] = Field(sa_column=Column(GUID, ForeignKey("BatteryCompany.id", ondelete="set null")))
    warranty_date: Optional[datetime]

    model: Optional[BatteryModel] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "BatteryInfo.model_id==BatteryModel.id",
        }
    )

    company: Optional[BatteryCompany] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "BatteryInfo.company_id==BatteryCompany.id",
        }
    )


class CompanyData(SQLModel):
    company_id: UUID = Field(
        sa_column=Column(GUID, ForeignKey("BatteryCompany.id", ondelete="cascade"), primary_key=True)
    )
    limit_size_fleet: Optional[int]
    ideal_size_fleet: Optional[int]


class BatteryReview(BaseUUIDModel):
    soh: Optional[float]
    remaining_life: Optional[float]
    price: Optional[float]


class BatteryStateEnum(str, Enum):
    USE = auto()
    TO_REPAIR = auto()
    REPAIRING = auto()
    STORED = auto()
    TRANSPORT = auto()


class BatteryIncidentEnum(str, Enum):
    BROKEN_CONNECTOR = auto()
    NOT_CHARGING = auto()
    BMS_ERROR = auto()
    WATER_DAMAGE = auto()
    DEAD_BATTERY = auto()


class BatteryState(BaseUUIDModel):
    company_id: Optional[UUID] = Field(sa_column=Column(GUID, ForeignKey("BatteryCompany.id", ondelete="cascade")))
    local: Optional[str]
    state: Optional[BatteryStateEnum] = Field(sa_column=Column(VARCHAR))
    date: Optional[datetime]
    incident: Optional[BatteryIncidentEnum] = Field(sa_column=Column(VARCHAR))
    comment: Optional[str]

    company: Optional[BatteryCompany] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "BatteryState.company_id==BatteryCompany.id",
        }
    )


class BatteryStatusEnum(str, Enum):
    VERY_GOOD = auto()
    GOOD = auto()
    BAD = auto()
    CRITICAL = auto()


class BatteryEvolution(BaseUUIDModel):
    date: Optional[datetime]
    capacity: Optional[float]
    status: Optional[BatteryStatusEnum] = Field(sa_column=Column(VARCHAR))
    sohr: Optional[float]
    sohcap: Optional[float]
    remaining_life: Optional[float]
    value: Optional[int]
