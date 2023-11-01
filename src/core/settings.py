from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, FilePath, PostgresDsn, RedisDsn, validator


class Settings(BaseSettings):
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/{API_VERSION}"
    PROJECT_NAME: str = "oniverse-api"
    JWT_EXPIRE_MINUTES: int = 60 * 1  # 1 hour
    WEB_CONCURRENCY = 9
    DB_POOL_SIZE = 83
    POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)
    MAX_OVERFLOW = 64

    DB_USER: str = "data"
    DB_PASSWORD: str = "data"
    DB_HOST: str = "localhost"
    DB_PORT: Union[int, str] = 5432
    DB_NAME: str = "data"
    DB_ECHO: bool = False
    DB_URL: Optional[str]
    ASYNC_DB_URL: Optional[str]

    @validator("ASYNC_DB_URL", pre=True)
    def assemble_async_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=str(values.get("DB_PORT")),
            path=f"/{values.get('DB_NAME') or ''}",
        )

    @validator("DB_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=str(values.get("DB_PORT")),
            path=f"/{values.get('DB_NAME') or ''}",
        )

    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # MINIO_ROOT_USER: str
    # MINIO_ROOT_PASSWORD: str
    # MINIO_URL: str
    # MINIO_BUCKET: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_USER: Optional[str]
    REDIS_PASSWORD: Optional[str]
    REDIS_URL: Optional[str]

    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            user=values.get("REDIS_USER"),
            password=values.get("REDIS_PASSWORD"),
            host=values.get("REDIS_HOST"),
            port=str(values.get("REDIS_PORT")),
        )

    SECRET_KEY: str = "KJMAgRxFdlijZPU8KLLWiJYsebxcDxpTMZDDqGRjJZg"
    ENCRYPT_KEY: str = "q+Y0dzUKGhfDDpAYouIUqLsY/NBIQJ2NMKFWeqjxsk8="
    BACKEND_CORS_ORIGINS: Union[List[str], List[AnyHttpUrl]] = ["*"]
    ALGORITHM = "HS256"

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_CONF_URL: str = "https://accounts.google.com/.well-known/openid-configuration"

    FACEBOOK_CLIENT_ID: str = ""
    FACEBOOK_CLIENT_SECRET: str = ""
    FACEBOOK_CONF_URL: str = "https://www.facebook.com/.well-known/openid-configuration/"

    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_CONF_URL: str = "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"

    DISCORD_CLIENT_ID: str = ""
    DISCORD_CLIENT_SECRET: str = ""
    DISCORD_CONF_URL: str = "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    LOG_LEVEL: str = "info"

    @validator("LOG_LEVEL", pre=True)
    def log_level(cls, v: str) -> str:
        return v.upper()

    DYNAMICS_PUBLIC_KEY_FILE: FilePath


settings = Settings()
