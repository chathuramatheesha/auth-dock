from typing import Annotated

from fastapi import Depends

from auth_dock.auth.services import AuthService
from auth_dock.users import UserServiceDep


def __get_auth_service(user_service: UserServiceDep) -> AuthService:
    return AuthService(user_service)


AuthServiceDep = Annotated[AuthService, Depends(__get_auth_service)]
