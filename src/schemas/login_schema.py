from core.security import Token
from schemas.user_schema import IUserRead


class IUserAuthInfo(Token):
    user_info: IUserRead
