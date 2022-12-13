from typing import Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.engine.url import URL

from api.jobs.models import JobModel, JobUpdate
from crud.schema import BaseApiOut, ItemListSchema, Paginator
from services.scheduler import AsyncScheduler, gen_scheduler, Schedule
from settings import settings


router = APIRouter(prefix="/jobs")


@router.get(
    "/schedules",
    response_model=BaseApiOut[ItemListSchema[Schedule]],
    include_in_schema=True,
)
async def get_schedules(
    paginator: Paginator = Depends(Paginator(perPage_max=100)), scheduler: AsyncScheduler = Depends(gen_scheduler)
):  # type: ignore
    schedules = await scheduler.get_schedules()
    start = (paginator.page - 1) * paginator.perPage
    end = paginator.page * paginator.perPage
    data = ItemListSchema(items=schedules[start:end])
    data.total = len(schedules) if paginator.show_total else None
    return BaseApiOut(data=data)


# @router.post(
#     "/job/{job_id}",
#     response_model=BaseApiOut[JobModel],
#     include_in_schema=True,
# )
# async def modify_job(
#     job_id: str = Path(...),
#     action: Literal["auto", "remove", "pause", "resume"] = None,
#     data: JobUpdate = Body(default=None),  # type: ignore
#     scheduler: AsyncScheduler = Depends(gen_scheduler),
# ):
#     job = scheduler.get_job(job_id)
#     if job:
#         if action is None:
#             job.modify(**data.dict(exclude_unset=True))
#         elif action == "auto":
#             job.pause() if job.next_run_time else job.resume()
#         elif action == "pause":
#             job.pause()
#         elif action == "resume":
#             job.resume()
#         elif action == "remove":
#             job.remove()
#     return BaseApiOut(data=JobModel.parse_job(job))
