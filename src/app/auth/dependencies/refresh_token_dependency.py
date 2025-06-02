from typing import Annotated

from argon2 import Type
from fastapi import Depends

from app.core import Argon2Hasher
from app.db.dependencies import SessionDep
from ..repositories.refresh_token_repository import RefreshTokenRepository
from ..services.refresh_token_service import RefreshTokenService


async def __get_argon2_hasher() -> Argon2Hasher:
    return Argon2Hasher(
        time_cost=1,
        memory_cost=32 * 1024,
        parallelism=1,
        hash_len=32,
        salt_len=16,
        type_=Type.ID,
    )


__Argon2Dep = Annotated[Argon2Hasher, Depends(__get_argon2_hasher)]


async def __get_refresh_token_repo(db: SessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)


__RefreshTokenRepoDep = Annotated[
    RefreshTokenRepository, Depends(__get_refresh_token_repo)
]


async def __get_refresh_token_service(
    repo: __RefreshTokenRepoDep, hasher: __Argon2Dep
) -> RefreshTokenService:
    return RefreshTokenService(repo, hasher)


RefreshTokenServiceDep = Annotated[
    RefreshTokenService, Depends(__get_refresh_token_service)
]
