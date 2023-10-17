from datetime import datetime, timedelta
from typing import Any, Union

from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext

from core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(str.encode(settings.ENCRYPT_KEY))

ALGORITHM = "HS256"


def create_token(subject: Union[str, Any], expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# def create_id_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
#     if not expires_delta:
#         expires_delta = timedelta(days=1)
#     return create_token(token_type='id', subject=subject, expires_delta=expires_delta)


# def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
#     if not expires_delta:
#         expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     return create_token(token_type='access', subject=subject, expires_delta=expires_delta)


# def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
#     if not expires_delta:
#         expires_delta = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
#     return create_token(token_type='refresh', subject=subject, expires_delta=expires_delta)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_data_encrypt(data) -> str:
    data = fernet.encrypt(data)
    return data.decode()


def get_content(variable: str) -> str:
    return fernet.decrypt(variable.encode()).decode()
