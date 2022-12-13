from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import URL
from apscheduler.datastores.async_sqlalchemy import AsyncSQLAlchemyDataStore
from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker
from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler import CoalescePolicy
from pydantic import BaseModel
from typing import Generator, Dict, List, Optional, Any
from datetime import datetime, timedelta
from settings import settings

from services.database import scheduler_async_engine

class Schedule(BaseModel):
    """
    Represents a schedule on which a task will be run.

    :var str id: the unique identifier of this schedule
    :var str task_id: unique identifier of the task to be run on this schedule
    :var tuple args: positional arguments to pass to the task callable
    :var dict[str, Any] kwargs: keyword arguments to pass to the task callable
    :var CoalescePolicy coalesce: determines what to do when processing the schedule if
        multiple fire times have become due for this schedule since the last processing
    :var ~datetime.timedelta | None misfire_grace_time: maximum number of seconds the
        scheduled job's actual run time is allowed to be late, compared to the scheduled
        run time
    :var ~datetime.timedelta | None max_jitter: maximum number of seconds to randomly
        add to the scheduled time for each job created from this schedule
    :var frozenset[str] tags: strings that can be used to categorize and filter the
        schedule and its derivative jobs
    :var ConflictPolicy conflict_policy: determines what to do if a schedule with the
        same ID already exists in the data store
    :var ~datetime.datetime next_fire_time: the next time the task will be run
    :var ~datetime.datetime | None last_fire_time: the last time the task was scheduled
        to run
    :var str | None acquired_by: ID of the scheduler that has acquired this schedule for
        processing
    :var str | None acquired_until: the time after which other schedulers are free to
        acquire the schedule for processing even if it is still marked as acquired
    """

    id: str
    task_id: str
    args: tuple
    kwargs: Dict[str, Any]
    coalesce: CoalescePolicy
    misfire_grace_time: Optional[timedelta]
    max_jitter: Optional[timedelta]
    tags: List[str]
    next_fire_time: Optional[datetime]
    last_fire_time: Optional[datetime]
    acquired_by: Optional[str]
    acquired_until: Optional[datetime]

data_store = AsyncSQLAlchemyDataStore(scheduler_async_engine)
event_broker = AsyncpgEventBroker.from_async_sqla_engine(scheduler_async_engine)

async def gen_scheduler() -> Generator[AsyncScheduler, None, None]:
    async with AsyncScheduler(data_store, event_broker) as scheduler:
        yield scheduler