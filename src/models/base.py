from typing import Any, Tuple

import inflection
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship as _relationship
from sqlalchemy.sql import func
from sqlservice import ModelBase, as_declarative

__all__ = [
    "Base",
    "relationship",
    "UUID_LEN",
    "ID_LEN",
    "SHORT_ID_LEN",
    "WORD_LEN",
    "EMAIL_LEN",
    "LINE_LEN",
    "TEXT_LEN",
    "KEY_LEN",
]


@as_declarative()
class Base(ModelBase):
    """
    Base class for all models

    It has some very cool methods which allows you
    to ship autocompletion and type verification to SQLAlchemy models.

    >>> class Model(Base):
    >>>     name = sa.Column(sa.String())
    >>>
    >>>     @classmethod
    >>>     def get_by_name(cls, name: str) -> sa.sql.Select:
    >>>         return Model.select_query(cls.id).where(cls.name == name)
    ...
    >>> session.fetchall(Model.get_by_name("random_name"))

    `created_at` and `updated_at` columns are created automatically for all models.

    Basic settings form models such as `__name__`, `__table__` and `__table_args__`
    defined with types to allow mypy verify this data.

    `__tablename__` generated automatically based on class name.
    """

    __name__: str
    __table__: sa.Table
    __table_args__: Tuple[Any, ...]

    @declared_attr
    def __tablename__(self) -> str:
        return inflection.underscore(self.__name__)

    @declared_attr
    def created_at(self) -> Any:
        return sa.Column(
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )

    @declared_attr
    def updated_at(self) -> Any:
        return sa.Column(
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )

    # @declared_attr
    # def __dict_args__(cls):
    #     """Per model configuration of :meth:`to_dict` serialization options."""
    #     return {"adapters": {
    #         datetime.datetime: str,
    #         datetime.date: datetime.date.isoformat,
    #         enum.Enum: lambda v: v.name,
    #     }}

    # @overload
    # def to_dict(self) -> Dict[str, Any]:
    #     jdict = super().to_dict()
    #     for k, v in jdict.items():
    #         if isinstance(v, datetime.datetime):
    #             jdict[k] = str(v)
    #         if isinstance(v, datetime.date):
    #             jdict[k] = v.isoformat()
    #         if isinstance(v, enum.Enum):
    #             jdict[k] = v.name
    #         if isinstance(v, dict):
    #             jdict[k] = self.to_dict(v)
    #     return jdict


def relationship(*arg, **kw):
    """A override for :func:`relationship`."""
    if "lazy" not in kw:
        kw["lazy"] = "selectin"
    if "uselist" not in kw:
        kw["uselist"] = False
    return _relationship(*arg, **kw)


UUID_LEN = 36
ID_LEN = 22
SHORT_ID_LEN = 10
WORD_LEN = 28
EMAIL_LEN = 72
LINE_LEN = 80
TEXT_LEN = 255
KEY_LEN = 1024

INDEX_KEY_COLLATION_ARGS = {"collation": "C"}
