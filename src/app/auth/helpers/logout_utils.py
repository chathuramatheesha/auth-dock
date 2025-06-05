from datetime import timezone, datetime

from app.core import ULID
from ..dtos import BlacklistedTokenDTO
from ..enums import BlacklistReason, TokenType
from ..exceptions.token_exceptions import (
    JWTTokenInvalidError,
    JWTTokenExpiredError,
    JWTTokenCredentialsInvalidError,
)
from ..services.blacklisted_token_service import BlacklistedTokenService
from ..services.jwt_service import JWTService
from ..services.refresh_token_service import RefreshTokenService


async def blacklist_access_token(
    jti: str, token_service: BlacklistedTokenService
) -> None:
    await token_service.add_token(
        BlacklistedTokenDTO(
            jti=ULID(jti),
            reason=BlacklistReason.LOGOUT,
            blacklisted_at=datetime.now(timezone.utc),
        )
    )


async def blacklist_refresh_token(
    jti: str, blacklisted_token_service: BlacklistedTokenService
) -> None:
    await blacklisted_token_service.add_token(
        BlacklistedTokenDTO(
            jti=ULID(jti),
            reason=BlacklistReason.LOGOUT,
            blacklisted_at=datetime.now(timezone.utc),
        )
    )


async def delete_refresh_token(
    jti: str, refresh_token_service: RefreshTokenService
) -> None:
    await refresh_token_service.delete_token(ULID(jti))


async def decode_delete_refresh_token(
    refresh_token: str,
    jwt_service: JWTService,
    blacklisted_token_service: BlacklistedTokenService,
    refresh_token_service: RefreshTokenService,
) -> None:
    try:
        refresh_token_data = await jwt_service.decode_token(
            refresh_token,
            TokenType.REFRESH_TOKEN,
            verify_sub=False,
            verify_exp=False,
        )

        await blacklist_access_token(refresh_token_data.jti, blacklisted_token_service)
        await delete_refresh_token(refresh_token_data.jti, refresh_token_service)
    except (
        JWTTokenInvalidError,
        JWTTokenExpiredError,
        JWTTokenCredentialsInvalidError,
    ):
        pass
