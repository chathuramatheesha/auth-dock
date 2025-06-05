from datetime import timezone, datetime

from app.core import Argon2Hasher, ULID
from app.users.dtos import UserOutDTO
from app.users.exceptions import UserEmailNotFoundError
from app.users.service import UserService
from ..dtos import BlacklistedTokenDTO, RefreshTokenDTO
from ..enums import TokenType, BlacklistReason
from ..exceptions.auth_exceptions import (
    AuthInvalidCredentialsError,
    AuthAccountDeletedError,
    AuthAccountDeactivatedError,
)
from ..services.blacklisted_token_service import BlacklistedTokenService
from ..services.jwt_service import JWTService
from ..services.refresh_token_service import RefreshTokenService


async def validate_user_credentials(
    email: str,
    password: str,
    user_service: UserService,
    hasher: Argon2Hasher,
) -> UserOutDTO:
    try:
        user = await user_service.get_user_by_email(email)

        if not await hasher.verify(password, user.hashed_password):
            raise AuthInvalidCredentialsError()

        if user.is_deleted:
            raise AuthAccountDeletedError()

        if not user.is_active:
            raise AuthAccountDeactivatedError()

        return user

    except UserEmailNotFoundError:
        raise AuthInvalidCredentialsError()


async def blacklist_previous_access_token(
    access_token: str,
    jwt_service: JWTService,
    blacklisted_token_service: BlacklistedTokenService,
) -> None:
    if access_token:
        previous_access_token_dto = await jwt_service.decode_token(
            access_token,
            TokenType.ACCESS_TOKEN,
            verify_exp=False,
            verify_sub=False,
            verify_jti=False,
        )

        if previous_access_token_dto:
            await blacklisted_token_service.add_token(
                BlacklistedTokenDTO(
                    jti=ULID(previous_access_token_dto.jti),
                    reason=BlacklistReason.LOGIN,
                    blacklisted_at=datetime.now(timezone.utc),
                )
            )


async def delete_previous_refresh_token(
    refresh_token: str,
    jwt_service: JWTService,
    refresh_token_service: RefreshTokenService,
) -> None:
    if refresh_token:
        previous_refresh_token_dto = await jwt_service.decode_token(
            refresh_token,
            TokenType.REFRESH_TOKEN,
            verify_exp=False,
        )

        if previous_refresh_token_dto:
            await refresh_token_service.delete_token(
                ULID(previous_refresh_token_dto.jti)
            )


async def generate_and_save_new_tokens(
    user_id: ULID,
    ip: str,
    device_info: str,
    jwt_service: JWTService,
    refresh_token_service: RefreshTokenService,
) -> tuple[str, str]:
    new_access_token = await jwt_service.encode_token(
        str(user_id), TokenType.ACCESS_TOKEN.value
    )
    new_refresh_token = await jwt_service.encode_token(
        str(user_id),
        TokenType.REFRESH_TOKEN,
        ip=ip,
    )
    refresh_token_data = await jwt_service.decode_token(
        new_refresh_token,
        TokenType.REFRESH_TOKEN,
    )

    await refresh_token_service.save_refresh_token(
        RefreshTokenDTO(
            jti=ULID(refresh_token_data.jti),
            user_id=ULID(refresh_token_data.sub),
            hashed_token=new_refresh_token,
            created_at=refresh_token_data.iat,
            expires_at=refresh_token_data.exp,
            ip_address=ip,
            device_info=device_info,
        )
    )

    return new_access_token, new_refresh_token
