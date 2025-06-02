from typing import Annotated

from fastapi import Depends

from app.core import Argon2Dep
from app.db import SessionDep
from app.users.repository import UserRepository
from app.users.service import UserService


async def __get_user_repo(db: SessionDep) -> UserRepository:
    return UserRepository(db)


__UserRepoDep = Annotated[UserRepository, Depends(__get_user_repo)]


async def __get_user_service(repo: __UserRepoDep, hasher: Argon2Dep) -> UserService:
    return UserService(repo, hasher)


UserServiceDep = Annotated[UserService, Depends(__get_user_service)]
