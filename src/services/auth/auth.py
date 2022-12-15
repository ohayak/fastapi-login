import asyncio
import functools
import inspect
from collections.abc import Coroutine
from functools import cached_property
from typing import Any, Callable, Generic, Optional, Sequence, Tuple, Type, TypeVar, Union

from fastapi import Depends, FastAPI, HTTPException, Request, Response, params
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, select
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.websockets import WebSocket

from services.database import auth_async_engine

from .backends.base import BaseTokenStore
from .backends.db import DbTokenStore
from .models import Role, User, UserRoleLink

_UserModelT = TypeVar("_UserModelT", bound=User)


class OAuth2(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        return request.auth.backend.get_user_token(request)


class AuthBackend(AuthenticationBackend, Generic[_UserModelT]):
    def __init__(self, auth: "Auth", token_store: BaseTokenStore):
        self.auth = auth
        self.token_store = token_store

    @staticmethod
    def get_user_token(request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization") or request.cookies.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        return None if not authorization or scheme.lower() != "bearer" else token

    async def authenticate(self, request: Request) -> Tuple["Auth", Optional[_UserModelT]]:
        return self.auth, await self.auth.get_current_user(request)

    def attach_middleware(self, app: FastAPI):
        app.add_middleware(AuthenticationMiddleware, backend=self)


class Auth(Generic[_UserModelT]):
    user_model: Type[_UserModelT] = None
    db: Union[AsyncSession, Session] = None
    backend: AuthBackend[_UserModelT] = None

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        token_store: BaseTokenStore = None,
        user_model: Type[_UserModelT] = User,
        pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto"),
    ):
        self.user_model = user_model or self.user_model
        assert self.user_model, "user_model is None"
        self.db = db or self.db
        self.backend = self.backend or AuthBackend(self, token_store or DbTokenStore(self.db))
        self.pwd_context = pwd_context

    async def authenticate_user(self, username: str, password: Union[str, SecretStr]) -> Optional[_UserModelT]:
        user: User = await self.db.scalar(select(self.user_model).where(self.user_model.username == username))
        if user:
            pwd = password.get_secret_value() if isinstance(password, SecretStr) else password
            pwd2 = user.password.get_secret_value() if isinstance(user.password, SecretStr) else user.password
            if self.pwd_context.verify(pwd, pwd2):
                return user
        return None

    @cached_property
    def get_current_user(self):
        async def _get_current_user(request: Request) -> Optional[_UserModelT]:
            if request.scope.get("auth"):
                return request.scope.get("user")
            request.scope["auth"], request.scope["user"] = self, None
            token = self.backend.get_user_token(request)
            if not token:
                return None
            token_data = await self.backend.token_store.read_token(token)
            if token_data is not None:
                request.scope["user"]: _UserModelT = await self.db.get(self.user_model, token_data.id)
            return request.user

        return _get_current_user

    def requires(
        self,
        roles: Union[str, Sequence[str]] = None,
        groups: Union[str, Sequence[str]] = None,
        permissions: Union[str, Sequence[str]] = None,
        status_code: int = 403,
        redirect: str = None,
        response: Union[bool, Response] = None,
    ) -> Callable:  # sourcery no-metrics
        groups_ = (groups,) if not groups or isinstance(groups, str) else tuple(groups)
        roles_ = (roles,) if not roles or isinstance(roles, str) else tuple(roles)
        permissions_ = (permissions,) if not permissions or isinstance(permissions, str) else tuple(permissions)

        async def has_requires(user: _UserModelT) -> bool:
            return user and await self.db.run_sync(
                user.has_requires, roles=roles, groups=groups, permissions=permissions
            )

        async def depend(
            request: Request,
            user: _UserModelT = Depends(self.get_current_user),
        ) -> Union[bool, Response]:
            user_auth = request.scope.get("__user_auth__", None)
            if user_auth is None:
                request.scope["__user_auth__"] = {}
            cache_key = (groups_, roles_, permissions_)
            if cache_key not in request.scope["__user_auth__"]:
                if isinstance(user, params.Depends):
                    user = await self.get_current_user(request)
                result = await has_requires(user)
                request.scope["__user_auth__"][cache_key] = result
            if not request.scope["__user_auth__"][cache_key]:
                if response is not None:
                    return response
                code, headers = status_code, {}
                if redirect is not None:
                    code = 307
                    headers = {"location": request.url_for(redirect)}
                raise HTTPException(status_code=code, headers=headers)
            return True

        def decorator(func: Callable = None) -> Union[Callable, Coroutine]:
            if func is None:
                return depend
            if isinstance(func, Request):
                return depend(func)
            sig = inspect.signature(func)
            for idx, parameter in enumerate(sig.parameters.values()):  # noqa: B007
                if parameter.name in ["request", "websocket"]:
                    type_ = parameter.name
                    break
            else:
                raise Exception(f'No "request" or "websocket" argument on function "{func}"')

            if type_ == "websocket":
                # Handle websocket functions. (Always async)
                @functools.wraps(func)
                async def websocket_wrapper(*args: Any, **kwargs: Any) -> None:
                    websocket = kwargs.get("websocket", args[idx] if args else None)
                    assert isinstance(websocket, WebSocket)
                    user = await self.get_current_user(websocket)  # type: ignore
                    if not await has_requires(user):
                        await websocket.close()
                    else:
                        await func(*args, **kwargs)

                return websocket_wrapper

            elif asyncio.iscoroutinefunction(func):
                # Handle async request/response functions.
                @functools.wraps(func)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Response:
                    request = kwargs.get("request", args[idx] if args else None)
                    assert isinstance(request, Request)
                    response = await depend(request)
                    if response is True:
                        return await func(*args, **kwargs)
                    return response

                return async_wrapper

            else:
                # Handle sync request/response functions.
                @functools.wraps(func)
                def sync_wrapper(*args: Any, **kwargs: Any) -> Response:
                    request = kwargs.get("request", args[idx] if args else None)
                    assert isinstance(request, Request)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(loop.create_task(depend(request)))
                    if response is True:
                        return func(*args, **kwargs)
                    return response

                return sync_wrapper

        return decorator

    def _create_role_user_sync(self, session: Session, role_key: str = "admin") -> User:
        # create admin role
        role = session.scalar(select(Role).where(Role.key == role_key))
        if not role:
            role = Role(key=role_key, name=f"{role_key} role")
            session.add(role)
            session.flush()

        # create admin user
        user = session.scalar(
            select(self.user_model)
            .join(UserRoleLink, UserRoleLink.user_id == self.user_model.id)
            .where(UserRoleLink.role_id == role.id)
        )
        if not user:
            user = self.user_model(
                username=role_key,
                password=self.pwd_context.hash(role_key),
                roles=[role],
            )
            session.add(user)
            session.flush()
        return user

    async def create_role_user(self, role_key: str = "admin", commit: bool = True) -> User:
        user = await self.db.run_sync(self._create_role_user_sync, role_key)
        if commit:
            await self.db.commit()
        return user


auth = Auth(db=AsyncSession(auth_async_engine, expire_on_commit=False))
