from app.core import ULID
from app.users.dtos import UserOutDTO
from app.users.exceptions import UserIDNotFoundError, UserNotFoundError
from app.users.service import UserService
from ..dtos import JWTAccessTokenDTO, JWTRefreshTokenDTO, JWTEmailTokenDTO
from ..enums import TokenType
from ..exceptions.auth_exceptions import (
    AuthAccountDeletedError,
    AuthAccountDeactivatedError,
)
from ..services.jwt_service import JWTService


async def decode_token(
    token: str,
    token_type: TokenType,
    jwt_service: JWTService,
) -> JWTAccessTokenDTO | JWTRefreshTokenDTO | JWTEmailTokenDTO:
    return await jwt_service.decode_token(token, token_type)


async def get_user_or_auth_error(user_service: UserService, user_id: str) -> UserOutDTO:
    try:
        user = await user_service.get_user_by_id(ULID(user_id))

    except UserIDNotFoundError:
        raise UserNotFoundError()

    if user.is_deleted:
        raise AuthAccountDeletedError()

    if not user.is_active:
        raise AuthAccountDeactivatedError()

    return user
