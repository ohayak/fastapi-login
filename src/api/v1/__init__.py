from fastapi import APIRouter

from api.v1.endpoints import battery, cache, company, group, login, role, user

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(role.router, prefix="/role", tags=["role"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(group.router, prefix="/group", tags=["group"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(battery.router, prefix="/battery", tags=["battery"])
