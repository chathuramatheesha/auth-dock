from datetime import datetime, timezone

import ulid

from auth_dock.core import ULID, Argon2Hasher
from auth_dock.utils.dto_utils import db_to_dto
from . import exceptions
from .dtos import (
    UserCreateDTO,
    UserOutDTO,
    UserCreateInDTO,
    UserUpdateDTO,
)
from .enums import UserRole
from .repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository, hasher: Argon2Hasher) -> None:
        self.__repo = repo
        self.__hasher = hasher

    async def create_user(self, create_request_dto: UserCreateInDTO) -> UserOutDTO:
        email_exists = await self.__repo.get_by_email(create_request_dto.email)

        if email_exists:
            raise exceptions.user_email_already_exists_exception

        create_dto = UserCreateDTO(
            id=ulid.new(),
            fullname=create_request_dto.fullname,
            email=create_request_dto.email,
            hashed_password=await self.__hasher.hash(create_request_dto.password),
            role=UserRole.USER,
            created_at=datetime.now(timezone.utc),
        )
        created_user = await self.__repo.create(create_dto)

        if not created_user:
            raise exceptions.user_creation_failed_exception

        return await db_to_dto(created_user, UserOutDTO)

    async def get_user_by_id(self, user_id: ULID) -> UserOutDTO | None:
        user = await self.__repo.get_by_id(user_id)

        if not user:
            return None

        return await db_to_dto(user, UserOutDTO)

    async def get_user_by_email(self, email: str) -> UserOutDTO | None:
        user = await self.__repo.get_by_email(email)

        if not user:
            return None

        return await db_to_dto(user, UserOutDTO)

    async def update_user(
        self,
        user_id: ULID,
        update_dto: UserUpdateDTO,
    ) -> UserOutDTO:
        user = await self.__repo.get_by_id(user_id)

        if not user:
            raise exceptions.user_not_found_exception

        updated_user = await self.__repo.update(user_id, update_dto)

        if not updated_user:
            return await db_to_dto(user, UserOutDTO)

        return await db_to_dto(updated_user, UserOutDTO)

    async def deactivate_user(self, user_id: ULID) -> None:
        await self.update_user(user_id, UserUpdateDTO(is_active=True))
        return

    async def soft_delete_user(self, user_id: ULID) -> None:
        await self.update_user(user_id, UserUpdateDTO(is_deleted=True))
        return

    async def delete_user_permanently(self, user_id: ULID) -> None:
        return await self.__repo.delete(user_id)
