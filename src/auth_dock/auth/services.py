from auth_dock.users.dtos import UserCreateInDTO, UserOutDTO
from auth_dock.users.service import UserService


class AuthService:
    def __init__(self, user_service: UserService) -> None:
        self.__user_service = user_service

    async def register_user(self, create_dto: UserCreateInDTO) -> UserOutDTO:
        return await self.__user_service.create_user(create_dto)
