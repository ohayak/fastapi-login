from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator


class Settings(BaseSettings):
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/{API_VERSION}"
    PROJECT_NAME: str = "bib-monitor"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 1  # 1 hour
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 100  # 100 days
    WEB_CONCURRENCY = 9
    DB_POOL_SIZE = 83
    POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)

    DB_AUTH_USER: str = "auth"
    DB_AUTH_PASSWORD: str = "auth"
    DB_AUTH_HOST: str = "localhost"
    DB_AUTH_PORT: Union[int, str] = 5432
    DB_AUTH_NAME: str = "auth"
    ASYNC_DB_AUTH_URI: Optional[str]

    DB_DATA_USER: str = "data"
    DB_DATA_PASSWORD: str = "data"
    DB_DATA_HOST: str = "localhost"
    DB_DATA_PORT: Union[int, str] = 5432
    DB_DATA_NAME: str = "data"
    ASYNC_DB_DATA_URI: Optional[str]
    DB_DATA_URI: Optional[str]

    @validator("ASYNC_DB_AUTH_URI", pre=True)
    def assemble_async_db_auth_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DB_AUTH_USER"),
            password=values.get("DB_AUTH_PASSWORD"),
            host=values.get("DB_AUTH_HOST"),
            port=str(values.get("DB_AUTH_PORT")),
            path=f"/{values.get('DB_AUTH_NAME') or ''}",
        )

    @validator("ASYNC_DB_DATA_URI", pre=True)
    def assemble_async_db_data_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DB_DATA_USER"),
            password=values.get("DB_DATA_PASSWORD"),
            host=values.get("DB_DATA_HOST"),
            port=str(values.get("DB_DATA_PORT")),
            path=f"/{values.get('DB_DATA_NAME') or ''}",
        )

    @validator("DB_DATA_URI", pre=True)
    def assemble_db_data_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("DB_DATA_USER"),
            password=values.get("DB_DATA_PASSWORD"),
            host=values.get("DB_DATA_HOST"),
            port=str(values.get("DB_DATA_PORT")),
            path=f"/{values.get('DB_DATA_NAME') or ''}",
        )

    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # MINIO_ROOT_USER: str
    # MINIO_ROOT_PASSWORD: str
    # MINIO_URL: str
    # MINIO_BUCKET: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"

    SECRET_KEY: str = "KJMAgRxFdlijZPU8KLLWiJYsebxcDxpTMZDDqGRjJZg"
    ENCRYPT_KEY: str = "q+Y0dzUKGhfDDpAYouIUqLsY/NBIQJ2NMKFWeqjxsk8="
    BACKEND_CORS_ORIGINS: Union[List[str], List[AnyHttpUrl]] = ["*"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


settings = Settings()
