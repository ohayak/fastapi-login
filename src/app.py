import logging
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from settings import settings


from api import router

app = FastAPI(title="bib-api", version="0.0.1", root_path=settings.root_path)
app.include_router(router)


@app.get("/")
def welcome(request: Request):
    return f"Welcome to {app.title} v{app.version}"


@app.get("/status")
def status(request: Request):
    database_status = "OK"

    # try:
    #     db.db.execute("SELECT 1")
    # except Exception as e:
    #     logging.exception(e)
    #     database_status = "KO"

    return {"root_path": request.scope.get("root_path"), "database": database_status}


if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup() -> None:
    return


@app.on_event("shutdown")
async def shutdown() -> None:
    return
