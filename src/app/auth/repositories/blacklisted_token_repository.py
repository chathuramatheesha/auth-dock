from dataclasses import asdict

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import ULID
from app.db import handle_db_exceptions
from ..dtos import BlacklistedTokenDTO
from ..models import BlacklistedToken


class BlacklistedTokenRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.__db = db

    @handle_db_exceptions
    async def add_token(self, create_dto: BlacklistedTokenDTO) -> BlacklistedToken:
        stmt = (
            insert(BlacklistedToken)
            .values(**asdict(create_dto))
            .returning(BlacklistedToken)
        )
        added_token = await self.__db.scalar(stmt)
        await self.__db.commit()
        return added_token

    @handle_db_exceptions
    async def delete_token(self, jti: ULID) -> None:
        stmt = delete(BlacklistedToken).where(BlacklistedToken.jti == jti)
        await self.__db.execute(stmt)
        await self.__db.commit()
        return

    @handle_db_exceptions
    async def get_by_jti(self, jti: ULID) -> BlacklistedToken | None:
        stmt = select(BlacklistedToken).where(BlacklistedToken.jti == jti)
        return await self.__db.scalar(stmt)
