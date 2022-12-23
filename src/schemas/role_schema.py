from enum import Enum
from models.role_model import RoleBase
from utils.partial import optional
from uuid import UUID


class IRoleCreate(RoleBase):
    pass


# All these fields are optional
@optional
class IRoleUpdate(RoleBase):
    pass

class IRoleRead(RoleBase):
    id: UUID

class IRoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    operator = "operator"