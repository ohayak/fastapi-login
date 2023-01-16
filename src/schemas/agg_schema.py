from typing import List

from pydantic import BaseModel

from schemas.battery_schema import IBatteryEvolutionRead
from utils.partial import optionalany


class AggRequestForm(BaseModel):
    group_by: List[str]
    avg: List[str] = []
    sum: List[str] = []
    min: List[str] = []
    max: List[str] = []
    count: List[str] = []


@optionalany
class IBatteryEvolutionAgg(IBatteryEvolutionRead):
    pass
