from datetime import datetime, timezone

from fastapi.security import HTTPAuthorizationCredentials

from app.core import Argon2Hasher, ULID
from app.schemas import MessageOutDTO
from app.users.dtos import UserCreateInDTO, UserOutDTO, UserUpdateDTO
from app.users.service import UserService
from app.utils.dto_utils import db_to_dto
from .blacklisted_token_service import BlacklistedTokenService
from .jwt_service import JWTService
from .refresh_token_service import RefreshTokenService
from ..constants import auth_constants
from ..dtos import AuthTokensOutDTO, AuthLoginInDTO, RefreshTokenDTO
from ..dtos import BlacklistedTokenDTO
from ..enums import TokenType, BlacklistReason
from ..exceptions import auth_exceptions


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        jwt_service: JWTService,
        refresh_token_service: RefreshTokenService,
        blacklisted_token_service: BlacklistedTokenService,
        hasher: Argon2Hasher,
    ) -> None:
        self.__user_service = user_service
        self.__jwt_service = jwt_service
        self.__refresh_token_service = refresh_token_service
        self.__blacklisted_token_service = blacklisted_token_service
        self.__hasher = hasher

    async def __update_last_login(self, user_id: ULID) -> None:
        await self.__user_service.update_user(
            user_id=user_id,
            update_dto=UserUpdateDTO(last_login_at=datetime.now(timezone.utc)),
        )
        return

    async def signup(self, create_dto: UserCreateInDTO) -> UserOutDTO:
        return await self.__user_service.create_user(create_dto)

    async def login(self, login_request: AuthLoginInDTO) -> AuthTokensOutDTO:
        user = await self.__user_service.get_user_by_email(login_request.email)

        if not user or not await self.__hasher.verify(
            login_request.password, user.hashed_password
        ):
            raise auth_exceptions.auth_invalid_credentials_exception

        if user.is_deleted:
            raise auth_exceptions.auth_deleted_account_exception

        if not user.is_active:
            raise auth_exceptions.auth_deactivate_account_exception

        if login_request.previous_refresh_token is not None:
            previous_refresh_token_dto = (
                await self.__jwt_service.decode_refresh_token_ignore_exceptions(
                    login_request.previous_refresh_token
                )
            )

            if previous_refresh_token_dto:
                await self.__refresh_token_service.delete_token(
                    ULID(previous_refresh_token_dto.jti)
                )

        access_token = await self.__jwt_service.encode_token(
            str(user.id), TokenType.ACCESS_TOKEN.value
        )
        refresh_token = await self.__jwt_service.encode_token(
            str(user.id),
            TokenType.REFRESH_TOKEN,
            ip=login_request.ip_address,
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
                ip_address=login_request.ip_address,
                device_info=login_request.device_info,
            )
        )
        await self.__update_last_login(user.id)

        return AuthTokensOutDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def logout(
        self,
        access_token: str,
        refresh_token: str,
        current_user: UserOutDTO,
    ) -> MessageOutDTO:
        access_token_data = await self.__jwt_service.decode_token(
            access_token, TokenType.ACCESS_TOKEN
        )
        refresh_token_data = (
            await self.__jwt_service.decode_refresh_token_ignore_exceptions(
                refresh_token
            )
        )

        current_datetime = datetime.now(timezone.utc)

        if refresh_token_data:
            await self.__blacklisted_token_service.add_token(
                BlacklistedTokenDTO(
                    jti=ULID(refresh_token_data.jti),
                    reason=BlacklistReason.LOGOUT,
                    blacklisted_at=current_datetime,
                )
            )
            await self.__refresh_token_service.delete_token(
                ULID(refresh_token_data.jti)
            )

        await self.__blacklisted_token_service.add_token(
            BlacklistedTokenDTO(
                jti=ULID(access_token_data.jti),
                reason=BlacklistReason.LOGOUT,
                blacklisted_at=current_datetime,
            )
        )

        return MessageOutDTO(auth_constants.SUC_LOGOUT)

    async def authenticate_user(
        self, token: HTTPAuthorizationCredentials
    ) -> UserOutDTO:
        access_token_dto = await self.__jwt_service.decode_token(
            token.credentials, TokenType.ACCESS_TOKEN
        )

        blacklisted_token_exists_by_jti = (
            await self.__blacklisted_token_service.get_by_jti(
                ULID(access_token_dto.jti)
            )
        )

        if blacklisted_token_exists_by_jti is not None:
            raise auth_exceptions.auth_token_revoked_exception

        user = await self.__user_service.get_user_by_id(ULID(access_token_dto.sub))

        if not user:
            raise auth_exceptions.auth_token_invalid_exception

        if user.is_deleted:
            raise auth_exceptions.auth_deleted_account_exception

        if not user.is_active:
            raise auth_exceptions.auth_deactivate_account_exception

        return await db_to_dto(user, UserOutDTO)
