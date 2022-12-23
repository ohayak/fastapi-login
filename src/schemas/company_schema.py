from typing import List, Optional
from uuid import UUID

from models.company_model import CompanyBase
from utils.partial import optional

from .user_schema import IUserReadWithoutCompany


class ICompanyCreate(CompanyBase):
    pass


class ICompanyRead(CompanyBase):
    id: UUID


# All these fields are optional
@optional
class ICompanyUpdate(CompanyBase):
    pass


class ICompanyReadWithUsers(CompanyBase):
    id: UUID
    users: Optional[List[IUserReadWithoutCompany]] = []
