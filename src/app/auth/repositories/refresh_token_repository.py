from dataclasses import asdict
from typing import Sequence

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import ULID
from ..dtos import RefreshTokenDTO
from ..models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.__db = db

    async def save_token(self, create_dto: RefreshTokenDTO) -> RefreshToken:
        stmt = insert(RefreshToken).values(**asdict(create_dto)).returning(RefreshToken)
        inserted_refresh_token = await self.__db.scalar(stmt)
        await self.__db.commit()
        return inserted_refresh_token

    async def get_by_jti(self, jti: ULID) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.jti == jti)
        refresh_token = await self.__db.scalar(stmt)
        return refresh_token

    async def list_tokens_by_user_id(self, user_id: ULID) -> Sequence[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        result = await self.__db.scalars(stmt)
        return result.all()

    async def delete_token(self, jti: ULID) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.jti == jti)
        await self.__db.execute(stmt)
        await self.__db.commit()
        return
