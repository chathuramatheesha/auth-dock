from datetime import datetime, timezone, timedelta

from app.core import ULID
from ..dtos import (
    JWTAccessTokenDTO,
    JWTRefreshTokenDTO,
    RefreshAccessTokenInDTO,
    BlacklistedTokenDTO,
    RefreshTokenDTO,
)
from ..enums import TokenType, BlacklistReason
from ..exceptions.auth_exceptions import AuthTokenRevokedError, AuthTokenInvalidError
from ..exceptions.token_exceptions import (
    BlacklistedTokenNotFoundError,
    RefreshTokenNotFoundError,
)
from ..services.blacklisted_token_service import BlacklistedTokenService
from ..services.jwt_service import JWTService
from ..services.refresh_token_service import RefreshTokenService
from ...common import gather_with_exception_check


# REFRESH ACCESS TOKEN helper functions


# Decode the access and refresh tokens from the incoming request
# Returns both as DTOs (access can be expired)
async def get_token_dtos(
    jwt_service: JWTService,
    request_dto: RefreshAccessTokenInDTO,
) -> tuple[JWTAccessTokenDTO, JWTRefreshTokenDTO]:

    tasks = [
        jwt_service.decode_token(
            request_dto.access_token,
            TokenType.ACCESS_TOKEN,
            verify_exp=False,
        ),
        jwt_service.decode_token(
            request_dto.refresh_token,
            TokenType.REFRESH_TOKEN,
        ),
    ]

    access_token_dto, refresh_token_dto = await gather_with_exception_check(tasks)

    return access_token_dto, refresh_token_dto


# Check if the refresh token is blacklisted (revoked for any reason)
# Raises error if token is revoked
async def check_refresh_blacklist(
    token_service: BlacklistedTokenService,
    refresh_dto: JWTRefreshTokenDTO,
) -> None:
    try:
        token = await token_service.get_by_jti(ULID(refresh_dto.jti))
        raise AuthTokenRevokedError(TokenType.REFRESH_TOKEN, token.reason)
    except BlacklistedTokenNotFoundError:
        pass


# Check if access token is blacklisted
# If it’s not blacklisted for TOKEN_ROTATION, blacklist the refresh token too and raise an error
async def check_access_blacklist_or_rotation(
    token_service: BlacklistedTokenService,
    access_dto: JWTAccessTokenDTO,
    refresh_dto: JWTRefreshTokenDTO,
) -> None:
    try:
        token = await token_service.get_by_jti(ULID(access_dto.jti))
        if token.reason != BlacklistReason.TOKEN_ROTATION:
            await token_service.add_token(
                BlacklistedTokenDTO(
                    jti=ULID(refresh_dto.jti),
                    reason=BlacklistReason.TOKEN_ROTATION,
                    blacklisted_at=datetime.now(timezone.utc),
                )
            )
            raise AuthTokenRevokedError(
                TokenType.REFRESH_TOKEN, BlacklistReason.TOKEN_ROTATION
            )
    except BlacklistedTokenNotFoundError:
        pass


# Verify the refresh token exists, is valid, and matches device/ip
# If invalid or suspicious, blacklist it and raise an error
async def verify_refresh_token(
    refresh_token_service: RefreshTokenService,
    blacklisted_token_service: BlacklistedTokenService,
    request_dto: RefreshAccessTokenInDTO,
    refresh_dto: JWTRefreshTokenDTO,
) -> RefreshTokenDTO:
    try:
        token_db = await refresh_token_service.get_by_jti(ULID(refresh_dto.jti))
    except RefreshTokenNotFoundError:
        raise AuthTokenInvalidError()

    if not await refresh_token_service.verify_token(
        request_dto.refresh_token, token_db.hashed_token
    ):
        raise AuthTokenInvalidError()

    if (
        token_db.ip_address != request_dto.ip_address
        or token_db.device_info != request_dto.device_info
    ):
        await blacklisted_token_service.add_token(
            BlacklistedTokenDTO(
                jti=token_db.jti,
                reason=BlacklistReason.COMPROMISED_TOKEN,
                blacklisted_at=datetime.now(timezone.utc),
            )
        )
        raise AuthTokenRevokedError(
            TokenType.REFRESH_TOKEN, BlacklistReason.COMPROMISED_TOKEN
        )

    return token_db


async def debug_add_token(dto, token_service):
    result = await token_service.add_token(dto)
    print(f"Token added: {result}")
    return result


# Blacklist both access and refresh tokens due to rotation
async def blacklist_for_rotation(
    access_dto: JWTAccessTokenDTO,
    refresh_dto: JWTRefreshTokenDTO,
    token_service: BlacklistedTokenService,
) -> None:
    now = datetime.now(timezone.utc)

    await token_service.add_token(
        BlacklistedTokenDTO(
            jti=ULID(access_dto.jti),
            reason=BlacklistReason.TOKEN_ROTATION,
            blacklisted_at=now,
        )
    )

    await token_service.add_token(
        BlacklistedTokenDTO(
            jti=ULID(refresh_dto.jti),
            reason=BlacklistReason.TOKEN_ROTATION,
            blacklisted_at=now,
        )
    )


# If the refresh token is about to expire (less than 2 days), issue a new one and save it
# Returns the new token string, or None if not needed
async def rotate_refresh_token_if_needed(
    jwt_service: JWTService,
    refresh_token_service: RefreshTokenService,
    token_db: RefreshTokenDTO,
    request_dto: RefreshAccessTokenInDTO,
) -> str | None:
    now = datetime.now(timezone.utc)
    expires = token_db.expires_at.replace(tzinfo=timezone.utc)

    if expires - now >= timedelta(days=2):
        return None

    new_refresh_token = await jwt_service.encode_token(
        token_db.user_id,
        TokenType.REFRESH_TOKEN,
        ip=request_dto.ip_address,
    )

    new_dto = await jwt_service.decode_token(new_refresh_token, TokenType.REFRESH_TOKEN)

    await refresh_token_service.save_refresh_token(
        RefreshTokenDTO(
            user_id=ULID(new_dto.sub),
            jti=ULID(new_dto.jti),
            hashed_token=new_refresh_token,
            created_at=new_dto.iat,
            expires_at=new_dto.exp,
            ip_address=request_dto.ip_address,
            device_info=request_dto.device_info,
        )
    )

    return new_refresh_token
