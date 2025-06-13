# 🔐 Core utilities

# 📦 Shared schemas
from app.common.schemas import MessageOutDTO
from app.core import Argon2Hasher, ULID

# 👤 User domain
from app.users.dtos import UserCreateInDTO, UserOutDTO
from app.users.service import UserService
from app.utils.dto_utils import db_to_dto

# 🛠️ Auth Services
from .blacklisted_token_service import BlacklistedTokenService
from .jwt_service import JWTService
from .refresh_token_service import RefreshTokenService

# 📄 Auth Constants, Enums & Auth DTOs
from ..constants import auth_constants
from ..dtos import (
    AuthTokensOutDTO,
    AuthLoginInDTO,
)
from ..dtos.auth_dtos import RefreshAccessTokenInDTO
from ..enums import TokenType

# 🔄 Token Utility Functions
from ..helpers import decode_token, get_user_or_auth_error
from ..helpers.authenticate_user_utils import (
    validate_token_type,
    check_token_blacklist,
)
from ..helpers.login_utils import (
    validate_user_credentials,
    generate_and_save_new_tokens,
    blacklist_delete_tokens,
)
from ..helpers.logout_utils import (
    blacklist_delete_tokens_logout,
)
from ..helpers.refresh_token_util import (
    get_token_dtos,
    check_refresh_blacklist,
    check_access_blacklist_or_rotation,
    verify_refresh_token,
    blacklist_for_rotation,
    rotate_refresh_token_if_needed,
)
from ...common import gather_with_exception_check


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

    async def authenticate_user(self, token: str, token_type: TokenType) -> UserOutDTO:
        validate_token_type(token_type)
        token_dto = await decode_token(token, token_type, self.__jwt_service)

        await check_token_blacklist(
            self.__blacklisted_token_service,
            token_dto.jti,
            token_type,
        )
        user = await get_user_or_auth_error(self.__user_service, token_dto.sub)
        return await db_to_dto(user, UserOutDTO)

    async def signup(self, create_dto: UserCreateInDTO) -> UserOutDTO:
        return await self.__user_service.create_user(create_dto)

    async def login(self, login_request: AuthLoginInDTO) -> AuthTokensOutDTO:
        user = await validate_user_credentials(
            login_request.email,
            login_request.password,
            self.__user_service,
            self.__hasher,
        )

        await blacklist_delete_tokens(
            login_request.previous_access_token,
            login_request.previous_refresh_token,
            self.__jwt_service,
            self.__refresh_token_service,
            self.__blacklisted_token_service,
        )

        access_token, refresh_token = await generate_and_save_new_tokens(
            user.id,
            login_request.ip_address,
            login_request.device_info,
            self.__jwt_service,
            self.__refresh_token_service,
        )
        await self.__user_service.update_last_login(user.id)

        return AuthTokensOutDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def logout(self, access_token: str, refresh_token: str) -> MessageOutDTO:
        access_data = await decode_token(
            access_token, TokenType.ACCESS_TOKEN, self.__jwt_service
        )

        await blacklist_delete_tokens_logout(
            ULID(access_data.jti),
            refresh_token,
            self.__jwt_service,
            self.__blacklisted_token_service,
            self.__refresh_token_service,
        )

        return MessageOutDTO(auth_constants.SUC_LOGOUT)

    async def refresh_access_token(
        self, request_dto: RefreshAccessTokenInDTO
    ) -> AuthTokensOutDTO:
        access_token_dto, refresh_token_dto = await get_token_dtos(
            self.__jwt_service, request_dto
        )
        await get_user_or_auth_error(self.__user_service, refresh_token_dto.sub)
        await check_refresh_blacklist(
            self.__blacklisted_token_service, refresh_token_dto
        )
        await check_access_blacklist_or_rotation(
            self.__blacklisted_token_service, access_token_dto, refresh_token_dto
        )
        refresh_db = await verify_refresh_token(
            self.__refresh_token_service,
            self.__blacklisted_token_service,
            request_dto,
            refresh_token_dto,
        )
        await blacklist_for_rotation(
            access_token_dto,
            refresh_token_dto,
            self.__blacklisted_token_service,
        )

        new_access_token, new_refresh_token = await gather_with_exception_check(
            [
                self.__jwt_service.encode_token(refresh_db.jti, TokenType.ACCESS_TOKEN),
                rotate_refresh_token_if_needed(
                    self.__jwt_service,
                    self.__refresh_token_service,
                    refresh_db,
                    request_dto,
                ),
            ]
        )

        return AuthTokensOutDTO(
            access_token=new_access_token,
            refresh_token=new_refresh_token if new_refresh_token else None,
            token_type="bearer",
        )
