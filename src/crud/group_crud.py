from crud.base_crud import CRUDBase
from models.group_model import Group
from schemas.group_schema import IGroupCreate, IGroupUpdate


class CRUDGroup(CRUDBase[Group, IGroupCreate, IGroupUpdate]):
    pass


group = CRUDGroup(Group)
