from datetime import datetime
from typing import Any, List, Optional, Sequence, Union

from pydantic import EmailStr, SecretStr
from sqlalchemy import and_, func
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.selectable import Exists
from sqlmodel import SQLModel, Session, Relationship, select, Field


class UserRoleLink(SQLModel, table=True):
    __tablename__ = "auth_user_roles"
    user_id: int = Field(
        primary_key=True,
        foreign_key="auth_user.id"
    )
    role_id: int = Field(
        primary_key=True,
        foreign_key="auth_role.id",
    )


class UserGroupLink(SQLModel, table=True):
    __tablename__ = "auth_user_groups"
    user_id: int = Field(
        primary_key=True,
        foreign_key="auth_user.id"
    )
    group_id: int = Field(
        primary_key=True,
        foreign_key="auth_group.id",
    )


class GroupRoleLink(SQLModel, table=True):
    __tablename__ = "auth_group_roles"
    group_id: int = Field(
        primary_key=True,
        foreign_key="auth_group.id",
    )
    role_id: int = Field(
        primary_key=True,
        foreign_key="auth_role.id",
    )


class RolePermissionLink(SQLModel, table=True):
    __tablename__ = "auth_role_permissions"
    role_id: int = Field(
        primary_key=True,
        foreign_key="auth_role.id",
    )
    permission_id: int = Field(
        primary_key=True,
        foreign_key="auth_permission.id",
    )

class PasswordStr(SecretStr, str):
    pass

class User(SQLModel, table=True):
    """User"""

    __tablename__ = "auth_user"
    id: int = Field(default=None, primary_key=True, nullable=False)
    username: str = Field(max_length=32, unique=True, index=True, nullable=False)
    is_active: bool = Field(default=True)
    nickname: str = Field(None, max_length=40)
    password: PasswordStr = Field(max_length=128, nullable=False)
    email: EmailStr = Field(None, index=True, nullable=True)
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": func.now(), "server_default": func.now()},
    )

    roles: Optional[List["Role"]] = Relationship(link_model=UserRoleLink)
    groups: Optional[List["Group"]] = Relationship(link_model=UserGroupLink)

    @property
    def is_authenticated(self) -> bool:
        return self.is_active

    @property
    def display_name(self) -> str:
        return self.nickname or self.username

    @property
    def identity(self) -> str:
        return self.username

    def _exists_role(self, *role_whereclause: Any) -> Exists:
        # check user role
        user_role_ids = (
            select(Role.id)
            .join(UserRoleLink, (UserRoleLink.user_id == self.id) & (UserRoleLink.role_id == Role.id))
            .where(*role_whereclause)
        )
        # check user group
        role_group_ids = select(GroupRoleLink.group_id).join(Role, and_(*role_whereclause, Role.id == GroupRoleLink.role_id))
        group_user_ids = (
            select(UserGroupLink.user_id)
            .where(UserGroupLink.user_id == self.id)
            .where(UserGroupLink.group_id.in_(role_group_ids))
        )
        return user_role_ids.exists() | group_user_ids.exists()

    def _exists_roles(self, roles: List[str]) -> Exists:
        """
        Check if the user belongs to the specified user role, or belongs to a user group containing the specified user role
        Args:
            roles:

        Returns:

        """
        return self._exists_role(Role.key.in_(roles))

    def _exists_groups(self, groups: List[str]) -> Exists:
        """
        Check if the user belongs to the specified user group
        Args:
            groups:

        Returns:

        """
        group_ids = (
            select(Group.id)
            .join(UserGroupLink, (UserGroupLink.user_id == self.id) & (UserGroupLink.group_id == Group.id))
            .where(Group.key.in_(groups))
        )
        return group_ids.exists()

    def _exists_permissions(self, permissions: List[str]) -> Exists:
        """
        Checks if the user belongs to a user role with the specified permissions
        Args:
            permissions:

        Returns:

        """
        role_ids = select(RolePermissionLink.role_id).join(
            Permission, Permission.key.in_(permissions) & (Permission.id == RolePermissionLink.permission_id)
        )
        return self._exists_role(Role.id.in_(role_ids))

    def has_requires(
        self,
        session: Session,
        *,
        roles: Union[str, Sequence[str]] = None,
        groups: Union[str, Sequence[str]] = None,
        permissions: Union[str, Sequence[str]] = None,
    ) -> bool:
        """
        Check if the user has the specified RBAC permissions
        Args:
            session: sqlalchemy `Session`;异步`AsyncSession`,请使用`run_sync`方法.
            roles: role list
            groups: user group list
            permissions: permission list

        Returns:
            The check is successful and returns `True`
        """
        if not groups and not roles and not permissions:
            return True
        stmt = select(1)
        if groups:
            groups_list = [groups] if isinstance(groups, str) else list(groups)
            stmt = stmt.where(self._exists_groups(groups_list))
        if roles:
            roles_list = [roles] if isinstance(roles, str) else list(roles)
            stmt = stmt.where(self._exists_roles(roles_list))
        if permissions:
            permissions_list = [permissions] if isinstance(permissions, str) else list(permissions)
            stmt = stmt.where(self._exists_permissions(permissions_list))
        return bool(session.scalar(stmt))


class BaseRBAC(SQLModel):
    __table_args__ = {"extend_existing": True}
    id: int = Field(default=None, primary_key=True, nullable=False)
    key: str = Field(max_length=40, unique=True, index=True, nullable=False)
    name: str = Field(default="", max_length=40)
    desc: str = Field(default="", max_length=400)


class Role(BaseRBAC, table=True):
    """Role"""

    __tablename__ = "auth_role"
    key: str = Field(max_length=40, unique=True, index=True, nullable=False)
    name: str = Field(default="", max_length=40)
    desc: str = Field(default="", max_length=400)
    groups: List["Group"] = Relationship(back_populates="roles", link_model=GroupRoleLink)
    permissions: List["Permission"] = Relationship(back_populates="roles", link_model=RolePermissionLink)


class Group(BaseRBAC, table=True):
    """Group"""
    __tablename__ = "auth_group"
    parent_id: Optional[int] = Field(
        None,
        foreign_key="auth_group.id",
    )
    roles: List["Role"] = Relationship(back_populates="groups", link_model=GroupRoleLink)


class Permission(BaseRBAC, table=True):
    """Permission"""

    __tablename__ = "auth_permission"
    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermissionLink)