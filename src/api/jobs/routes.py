from typing import List, Literal
from fastapi import APIRouter, Body, Path, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from datetime import timedelta, datetime
from api.jobs.models import JobModel, JobUpdate
from crud.schema import BaseApiOut, ItemListSchema, Paginator

from services.scheduler import get_scheduler, SchedulerClient
from settings import settings
from sqlalchemy.engine.url import URL




router = APIRouter()


@router.get(
    "/jobs",
    response_model=BaseApiOut[ItemListSchema[JobModel]],
    include_in_schema=True,
)
async def get_jobs(scheduler: SchedulerClient = Depends(get_scheduler), 
    paginator: Paginator = Depends(Paginator(perPage_max=100))):  # type: ignore
    jobs = scheduler.get_jobs()
    start = (paginator.page - 1) * paginator.perPage
    end = paginator.page * paginator.perPage
    data = ItemListSchema(items=[JobModel.parse_job(job) for job in jobs[start:end]])
    data.total = len(jobs) if paginator.show_total else None
    return BaseApiOut(data=data)

@router.post(
    "/job/{job_id}",
    response_model=BaseApiOut[JobModel],
    include_in_schema=True,
)
async def modify_job(
    job_id: str = Path(...),
    action: Literal["auto", "remove", "pause", "resume"] = None,
    data: JobUpdate = Body(default=None),  # type: ignore
    scheduler: SchedulerClient = Depends(get_scheduler)
):
    job = scheduler.get_job(job_id)
    if job:
        if action is None:
            job.modify(**data.dict(exclude_unset=True))
        elif action == "auto":
            job.pause() if job.next_run_time else job.resume()
        elif action == "pause":
            job.pause()
        elif action == "resume":
            job.resume()
        elif action == "remove":
            job.remove()
    return BaseApiOut(data=JobModel.parse_job(job))


@router.post(
    "/job",
    response_model=BaseApiOut[JobModel],
    include_in_schema=True,
)
async def add_job(
    data: JobUpdate = Body(default=None),  # type: ignore
    scheduler: SchedulerClient = Depends(get_scheduler)
):
    scheduler.add_job(data.)
    return BaseApiOut(data=JobModel.parse_job(job))