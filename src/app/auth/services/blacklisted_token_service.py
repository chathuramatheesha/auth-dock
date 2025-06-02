from app.core import ULID
from app.utils.dto_utils import db_to_dto
from ..dtos import BlacklistedTokenDTO
from ..repositories import BlacklistedTokenRepository


class BlacklistedTokenService:
    def __init__(self, repo: BlacklistedTokenRepository) -> None:
        self.__repo = repo

    async def add_token(self, create_dto: BlacklistedTokenDTO) -> BlacklistedTokenDTO:
        added_token = await self.__repo.add_token(create_dto)
        return await db_to_dto(added_token, BlacklistedTokenDTO)

    async def get_by_jti(self, jti: ULID) -> BlacklistedTokenDTO | None:
        token = await self.__repo.get_by_jti(jti)

        if not token:
            return None

        return await db_to_dto(token, BlacklistedTokenDTO)

    async def delete_token(self, jti: ULID) -> None:
        return await self.__repo.delete_token(jti)
