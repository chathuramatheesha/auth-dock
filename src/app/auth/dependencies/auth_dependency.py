from typing import Annotated

from fastapi import Depends

from app.auth.services import AuthService
from app.core import Argon2Dep
from app.users import UserServiceDep
from .jwt_dependency import JWTServiceDep
from .refresh_token_dependency import RefreshTokenServiceDep


def __get_auth_service(
    user_service: UserServiceDep,
    jwt_service: JWTServiceDep,
    refresh_token_service: RefreshTokenServiceDep,
    hasher: Argon2Dep,
) -> AuthService:
    return AuthService(
        user_service=user_service,
        jwt_service=jwt_service,
        refresh_token_service=refresh_token_service,
        hasher=hasher,
    )


AuthServiceDep = Annotated[AuthService, Depends(__get_auth_service)]
