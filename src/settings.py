from enum import Enum
from sys import stderr, stdout

from pydantic import BaseSettings, Field, validator


class AppMode(Enum):
    DEV = "development"
    PROD = "production"

class Settings(BaseSettings):
    # Application settings
    app_mode: AppMode = Field(default=AppMode.PROD)
    root_path: str = Field(default="")

    # DB settings

    db_auth_echo: str = Field(default=None)
    db_auth_driver: str = Field(default="postgresql+asyncpg")
    db_auth_user: str = Field(default="auth")
    db_auth_password: str = Field(default="auth")
    db_auth_host: str = Field(default="localhost")
    db_auth_port: int = Field(default=5432)
    db_auth_name: str = Field(default="auth")


    db_scheduler_echo: str = Field(default=None)
    db_scheduler_driver: str = Field(default="postgresql+asyncpg")
    db_scheduler_user: str = Field(default="scheduler")
    db_scheduler_password: str = Field(default="scheduler")
    db_scheduler_host: str = Field(default="localhost")
    db_scheduler_port: int = Field(default=5432)
    db_scheduler_name: str = Field(default="scheduler")

    # Server settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=False)
    workers: int = Field(default=1)
    enable_cors: bool = Field(default=True)


    log_level: str = Field(default="INFO")
    accesslog: bool = Field(default=False)
    errorlog: bool = Field(default=True)

    scheduler_rpc_host = Field(default="localhost")
    scheduler_rpc_port: int = Field(default=18812)


    @property
    def is_dev(self) -> bool:
        return self.app_mode == AppMode.DEV


settings = Settings()
