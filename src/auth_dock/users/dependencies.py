from typing import Annotated

from fastapi import Depends

from auth_dock.core import Argon2Dep
from auth_dock.db import SessionDep
from auth_dock.users.repository import UserRepository
from auth_dock.users.service import UserService


async def __get_user_repo(db: SessionDep) -> UserRepository:
    return UserRepository(db)


__UserRepoDep = Annotated[UserRepository, Depends(__get_user_repo)]


async def __get_user_service(repo: __UserRepoDep, hasher: Argon2Dep) -> UserService:
    return UserService(repo, hasher)


UserServiceDep = Annotated[UserService, Depends(__get_user_service)]
