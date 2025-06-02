from datetime import datetime, timezone

from fastapi import Request, Response

from app.core import Argon2Hasher, ULID
from app.users.dtos import UserCreateInDTO, UserOutDTO, UserUpdateDTO
from app.users.service import UserService
from .jwt_service import JWTService
from .refresh_token_service import RefreshTokenService
from ..dtos import AuthTokensOutDTO, AuthLoginInDTO, RefreshTokenDTO
from ..enums import TokenType
from ..exceptions import auth_exceptions


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        jwt_service: JWTService,
        refresh_token_service: RefreshTokenService,
        hasher: Argon2Hasher,
    ) -> None:
        self.__user_service = user_service
        self.__jwt_service = jwt_service
        self.__refresh_token_service = refresh_token_service
        self.__hasher = hasher

    async def __update_last_login(self, user_id: ULID) -> None:
        await self.__user_service.update_user(
            user_id=user_id,
            update_dto=UserUpdateDTO(last_login_at=datetime.now(timezone.utc)),
        )
        return

    async def signup(self, create_dto: UserCreateInDTO) -> UserOutDTO:
        return await self.__user_service.create_user(create_dto)

    async def login(
        self,
        request: Request,
        response: Response,
        login_request: AuthLoginInDTO,
    ) -> AuthTokensOutDTO:
        user = await self.__user_service.get_user_by_email(login_request.email)

        if not user or not await self.__hasher.verify(
            login_request.password,
            user.hashed_password,
        ):
            raise auth_exceptions.auth_invalid_credentials_exception

        if user.is_deleted:
            raise auth_exceptions.auth_deleted_account_exception

        if not user.is_active:
            raise auth_exceptions.auth_deactivate_account_exception

        # if not user.is_verified:
        #     raise exceptions.auth_verify_email_exception

        previous_refresh_token = request.cookies.get(TokenType.REFRESH_TOKEN.value)

        if previous_refresh_token:
            previous_refresh_token_data = await self.__jwt_service.decode_token(
                previous_refresh_token, TokenType.REFRESH_TOKEN
            )
            await self.__refresh_token_service.delete_token(
                ULID(previous_refresh_token_data.jti)
            )
            response.delete_cookie(TokenType.REFRESH_TOKEN.value)

        user_ip_address = request.client.host
        access_token = await self.__jwt_service.encode_token(
            str(user.id), TokenType.ACCESS_TOKEN.value
        )
        refresh_token = await self.__jwt_service.encode_token(
            str(user.id),
            TokenType.REFRESH_TOKEN,
            ip=user_ip_address,
            type=TokenType.REFRESH_TOKEN.value,
        )
        refresh_token_data = await self.__jwt_service.decode_token(
            refresh_token,
            TokenType.REFRESH_TOKEN,
        )

        await self.__refresh_token_service.save_refresh_token(
            RefreshTokenDTO(
                jti=ULID(refresh_token_data.jti),
                user_id=ULID(refresh_token_data.sub),
                hashed_token=refresh_token,
                created_at=refresh_token_data.iat,
                expires_at=refresh_token_data.exp,
                ip_address=user_ip_address,
                device_info=request.headers.get("user-agent"),
            )
        )
        await self.__update_last_login(user.id)

        return AuthTokensOutDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
