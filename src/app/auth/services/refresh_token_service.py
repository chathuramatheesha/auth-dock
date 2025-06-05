from app.core import Argon2Hasher, ULID
from app.utils.dto_utils import db_to_dto
from ..dtos import RefreshTokenDTO
from ..exceptions.token_exceptions import (
    RefreshTokenSaveFailedError,
    RefreshTokenNotFoundError,
)
from ..repositories.refresh_token_repository import RefreshTokenRepository


class RefreshTokenService:
    def __init__(self, repo: RefreshTokenRepository, hasher: Argon2Hasher) -> None:
        self.__repo = repo
        self.__hasher = hasher

    async def save_refresh_token(self, create_dto: RefreshTokenDTO) -> RefreshTokenDTO:
        create_dto.hashed_token = await self.__hasher.hash(create_dto.hashed_token)
        saved_refresh_token = await self.__repo.save_token(create_dto)

        if not saved_refresh_token:
            raise RefreshTokenSaveFailedError()

        return await db_to_dto(saved_refresh_token, RefreshTokenDTO)

    async def get_by_jti(self, jti: ULID) -> RefreshTokenDTO:
        token = await self.__repo.get_by_jti(jti)

        if not token:
            raise RefreshTokenNotFoundError(jti)

        return await db_to_dto(token, RefreshTokenDTO)

    async def verify_token(self, token: str, hashed_token: str) -> bool:
        return await self.__hasher.verify(token, hashed_token)

    async def delete_token(self, jti: ULID) -> None:
        return await self.__repo.delete_token(jti)
