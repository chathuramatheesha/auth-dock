from typing import Annotated

from fastapi import Depends

from app.db import SessionDep
from ..repositories import BlacklistedTokenRepository
from ..services import BlacklistedTokenService


async def _get_blacklisted_token_repo(db: SessionDep) -> BlacklistedTokenRepository:
    return BlacklistedTokenRepository(db)


_BlacklistedTokenRepoDep = Annotated[
    BlacklistedTokenRepository, Depends(_get_blacklisted_token_repo)
]


async def _get_blacklisted_token_service(
    repo: _BlacklistedTokenRepoDep,
) -> BlacklistedTokenService:
    return BlacklistedTokenService(repo)


BlacklistedTokenServiceDep = Annotated[
    BlacklistedTokenService, Depends(_get_blacklisted_token_service)
]
