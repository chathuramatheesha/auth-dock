from dataclasses import asdict
from typing import Sequence

from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import ULID
from app.utils.dto_utils import dto_to_update_db, is_dto_empty
from app.db import handle_db_exceptions
from .dtos import UserCreateDTO, UserUpdateDTO
from .models import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.__db = db

    @handle_db_exceptions
    async def get_by_id(self, user_id: ULID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        user = await self.__db.scalar(stmt)
        return user

    @handle_db_exceptions
    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        user = await self.__db.scalar(stmt)
        return user

    @handle_db_exceptions
    async def create_user(self, create_dto: UserCreateDTO) -> User:
        stmt = insert(User).values(**asdict(create_dto)).returning(User)
        inserted_user = await self.__db.scalar(stmt)
        await self.__db.commit()
        return inserted_user

    @handle_db_exceptions
    async def update_user(
        self, user_id: ULID, update_dto: UserUpdateDTO
    ) -> User | None:
        if await is_dto_empty(update_dto):
            return None

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**(await dto_to_update_db(update_dto)))
            .returning(User)
        )
        updated_user = await self.__db.scalar(stmt)
        await self.__db.commit()
        return updated_user

    @handle_db_exceptions
    async def delete_user(self, user_id: ULID) -> None:
        stmt = delete(User).where(User.id == user_id)
        await self.__db.execute(stmt)
        await self.__db.commit()
        return

    @handle_db_exceptions
    async def list_user(self) -> Sequence[User]:
        stmt = select(User)
        users = await self.__db.scalars(stmt)
        return users.all()
