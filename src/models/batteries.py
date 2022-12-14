from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Union

from sqlalchemy import and_, func, Column
from sqlalchemy.sql.selectable import Exists
from sqlmodel import Field, Relationship, Session, SQLModel, select
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.types import JSON



class BatteryModel(SQLModel, table=True):
    __tablename__ = "battery_model"
    id: int = Field(primary_key=True)
    name: str = Field(max_length=32)
    manufacturer: Optional[str] = Field(max_length=32)
    value: Optional[int]
    nominal_capacity: Optional[float]
    voltage: Optional[int]
    number_cells: Optional[int]
    configuration: Optional[str] = Field(max_length=10)
    weight: Optional[float]
    size: Dict[str, int] = Field(default={}, sa_column=Column(MutableDict.as_mutable(JSON)))
    cells_model: Optional[str] = Field(max_length=32)
    siliconned: Optional[bool]
    charger: Optional[bool]
    communicaing: Optional[bool]
    diag_tool: Optional[bool]
    msds_url: Optional[str]
    un38_3: Optional[str]
    attachements: Dict[str, int] = Field(default={}, sa_column=Column(MutableDict.as_mutable(JSON)))


class BatteryCell(SQLModel, table=True):
    __tablename__ = "battery_cell"
    id: int = Field(primary_key=True)
    name: str = Field(max_length=32)
    technology: Optional[str] = Field(max_length=32)
    nominal_capacity: Optional[float]
    attachements: Dict[str, int] = Field(default={}, sa_column=Column(MutableDict.as_mutable(JSON)))


class BatteryInfo(SQLModel, table=True):
    __tablename__ = "battery_info"
    id: int = Field(primary_key=True)
    name: str = Field(max_length=32)
    external_id: str = Field(max_length=32)
    battery_id: int = Field(foreign_key="battery_model.id")
    company: str = Field(max_length=32)

    model: BatteryModel = Relationship(link_model=BatteryModel)
