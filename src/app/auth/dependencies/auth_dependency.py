from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.services import AuthService
from app.core import Argon2Dep
from app.users import UserServiceDep
from app.users.dtos import UserOutDTO
from .blacklisted_token_dependency import BlacklistedTokenServiceDep
from .jwt_dependency import JWTServiceDep
from .refresh_token_dependency import RefreshTokenServiceDep
from ..enums import TokenType

security = HTTPBearer()

AuthTokenDep = Annotated[HTTPAuthorizationCredentials, Depends(security)]


def _get_auth_service(
    user_service: UserServiceDep,
    jwt_service: JWTServiceDep,
    refresh_token_service: RefreshTokenServiceDep,
    blacklisted_token_service: BlacklistedTokenServiceDep,
    hasher: Argon2Dep,
) -> AuthService:
    return AuthService(
        user_service=user_service,
        jwt_service=jwt_service,
        refresh_token_service=refresh_token_service,
        blacklisted_token_service=blacklisted_token_service,
        hasher=hasher,
    )


AuthServiceDep = Annotated[AuthService, Depends(_get_auth_service)]


async def _get_current_user(token: AuthTokenDep, service: AuthServiceDep) -> UserOutDTO:
    return await service.authenticate_user(token.credentials, TokenType.ACCESS_TOKEN)


AuthCurrentUserDep = Annotated[UserOutDTO, Depends(_get_current_user)]
