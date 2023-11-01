from uuid import UUID

from models.socialaccount_model import SocialAccountBase
from utils.partial import optional


class ISocialAccountCreate(SocialAccountBase):
    pass


class ISocialAccountCreateWithId(SocialAccountBase):
    id: UUID


# All these fields are optional
@optional
class ISocialAccountUpdate(SocialAccountBase):
    pass


class ISocialAccountRead(SocialAccountBase):
    pass
