from enum import Enum
from sys import stderr, stdout

from pydantic import BaseSettings, Field, validator


class AppMode(Enum):
    DEV = "development"
    PROD = "production"


class LogSink(Enum):
    STDOUT = "stdout"
    STDERR = "stderr"


class Settings(BaseSettings):
    # Application settings
    app_mode: AppMode = Field(default=AppMode.PROD)
    root_path: str = Field(default="")

    # DB settings
    db_migrate: bool = Field(default=False)
    db_echo: str = Field(default=None)
    db_driver: str = Field(default="postgresql")
    db_user: str = Field(default="coredata")
    db_password: str = Field(default="coredata")
    db_host: str = Field(default="coredata")
    db_port: int = Field(default=5432)
    db_name: str = Field(default="coredata")

    # Server settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=False)
    workers: int = Field(default=1)
    enable_cors: bool = Field(default=True)

    # Logging settings
    log_sink: LogSink = Field(default=LogSink.STDERR)
    log_level: str = Field(default="INFO")
    log_backtrace: bool = Field(default=True)
    log_diagnose: bool = Field(default=False)
    log_catch: bool = Field(default=False)
    log_serialize: bool = Field(default=False)

    accesslog: bool = Field(default=False)
    errorlog: bool = Field(default=True)

    @validator("log_sink")
    def set_log_sink(cls, v):
        return stdout if v == LogSink.STDOUT else stderr

    @property
    def is_dev(self) -> bool:
        return self.app_mode == AppMode.DEV


settings = Settings()
