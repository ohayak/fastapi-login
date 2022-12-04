from datetime import datetime
from typing import Any, Dict, List
from pydantic import Field

from pydantic import BaseModel, Field, validator

class JobModel(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    next_run_time: datetime = Field(None)
    trigger: str = Field(None)  # BaseTrigger
    func_ref: str = Field(...)
    args: List[Any] = Field(None)
    kwargs: Dict[str, Any] = Field(None)
    executor: str = Field("default")
    max_instances: int = Field(None)
    misfire_grace_time: int = Field(None)
    coalesce: bool = Field(None)

    @validator("trigger", pre=True)
    def trigger_valid(cls, v):  # sourcery skip: instance-method-first-arg-name
        return str(v)

    @classmethod
    def parse_job(cls, job):
        return job and cls(**{k: getattr(job, k, None) for k in cls.__fields__})

class JobUpdate(BaseModel):
    name: str = Field(None)
    next_run_time: datetime = Field(None)
