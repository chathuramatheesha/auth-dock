from app.core import Argon2Hasher, ULID
from app.utils.dto_utils import db_to_dto
from ..dtos import RefreshTokenDTO
from ..exceptions import token_exceptions
from ..repositories.refresh_token_repository import RefreshTokenRepository


class RefreshTokenService:
    def __init__(self, repo: RefreshTokenRepository, hasher: Argon2Hasher) -> None:
        self._repo = repo
        self._hasher = hasher

    async def save_refresh_token(self, create_dto: RefreshTokenDTO) -> RefreshTokenDTO:
        create_dto.hashed_token = await self._hasher.hash(create_dto.hashed_token)
        saved_refresh_token = await self._repo.save_token(create_dto)

        if not saved_refresh_token:
            raise token_exceptions.token_refresh_save_exception

        return await db_to_dto(saved_refresh_token, RefreshTokenDTO)

    async def delete_token(self, jti: ULID) -> None:
        return await self._repo.delete_token(jti)
