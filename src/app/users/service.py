from datetime import datetime, timezone

import ulid

from app.core import ULID, Argon2Hasher
from app.utils.dto_utils import db_to_dto
from .dtos import (
    UserCreateDTO,
    UserOutDTO,
    UserCreateInDTO,
    UserUpdateDTO,
)
from .enums import UserRole
from .exceptions import (
    UserEmailExistsError,
    UserCreateFailedError,
    UserIDNotFoundError,
    UserEmailNotFoundError,
    UserNotFoundError,
    UserUpdateFailedError,
)
from .repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository, hasher: Argon2Hasher) -> None:
        self.__repo = repo
        self.__hasher = hasher

    # CREATE User
    async def create_user(self, create_request_dto: UserCreateInDTO) -> UserOutDTO:
        # Check if email is already registered
        email_exists = await self.__repo.get_by_email(create_request_dto.email)

        if email_exists:
            raise UserEmailExistsError(create_request_dto.email)

        # Prepare data for new user creation
        create_dto = UserCreateDTO(
            id=ulid.new(),
            fullname=create_request_dto.fullname,
            email=create_request_dto.email,
            hashed_password=await self.__hasher.hash(create_request_dto.password),
            role=UserRole.USER,
            created_at=datetime.now(timezone.utc),
        )

        # Insert user into database
        created_user = await self.__repo.create_user(create_dto)

        if not created_user:
            raise UserCreateFailedError()

        # Convert DB model to output DTO and return
        return await db_to_dto(created_user, UserOutDTO)

    # SEARCH User by id
    async def get_user_by_id(self, user_id: ULID) -> UserOutDTO:
        user = await self.__repo.get_by_id(user_id)

        if not user:
            raise UserIDNotFoundError(user_id)

        return await db_to_dto(user, UserOutDTO)

    async def get_user_by_email(self, email: str) -> UserOutDTO:
        user = await self.__repo.get_by_email(email)

        if not user:
            raise UserEmailNotFoundError(email)

        return await db_to_dto(user, UserOutDTO)

    # UPDATE User
    async def update_user(
        self,
        user_id: ULID,
        update_dto: UserUpdateDTO,
    ) -> UserOutDTO:
        user = await self.__repo.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        updated_user = await self.__repo.update_user(user_id, update_dto)

        if not updated_user:
            raise UserUpdateFailedError()

        return await db_to_dto(updated_user, UserOutDTO)

    # UPDATE User's last_login
    async def update_last_login(self, user_id: ULID) -> None:
        await self.update_user(
            user_id=user_id,
            update_dto=UserUpdateDTO(last_login_at=datetime.now(timezone.utc)),
        )
        return

    # Deactivate User (is_active=False)
    async def deactivate_user(self, user_id: ULID) -> None:
        await self.update_user(user_id, UserUpdateDTO(is_active=True))
        return

    # DELETE User (Soft) (is_deleted=True)
    async def soft_delete_user(self, user_id: ULID) -> None:
        await self.update_user(user_id, UserUpdateDTO(is_deleted=True))
        return

    # DELETE User (Permanent)
    async def delete_user_permanently(self, user_id: ULID) -> None:
        return await self.__repo.delete_user(user_id)
