import asyncio
from datetime import timezone, datetime

from app.core import ULID
from ..dtos import BlacklistedTokenDTO, JWTRefreshTokenDTO
from ..enums import BlacklistReason, TokenType
from ..exceptions.token_exceptions import (
    JWTTokenInvalidError,
    JWTTokenExpiredError,
    JWTTokenCredentialsInvalidError,
)
from ..services.blacklisted_token_service import BlacklistedTokenService
from ..services.jwt_service import JWTService
from ..services.refresh_token_service import RefreshTokenService


async def decode_refresh_token(
    refresh_token: str, jwt_service: JWTService
) -> JWTRefreshTokenDTO | None:
    try:
        refresh_token_data = await jwt_service.decode_token(
            refresh_token,
            TokenType.REFRESH_TOKEN,
            verify_exp=False,
        )

        return refresh_token_data

    except (
        JWTTokenInvalidError,
        JWTTokenExpiredError,
        JWTTokenCredentialsInvalidError,
    ):
        return None


async def blacklist_token(jti: str, token_service: BlacklistedTokenService) -> None:
    await token_service.add_token(
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


async def blacklist_delete_tokens_logout(
    access_token_jti: ULID,
    refresh_token: str,
    jwt_service: JWTService,
    blacklisted_token_service: BlacklistedTokenService,
    refresh_token_service: RefreshTokenService,
) -> None:
    refresh_token_dto = await decode_refresh_token(refresh_token, jwt_service)

    if not access_token_jti and (not refresh_token_dto or not refresh_token_dto.jti):
        return

    tasks = []

    if refresh_token_dto and refresh_token_dto.jti:
        tasks.append(blacklist_token(refresh_token_dto.jti, blacklisted_token_service))
        tasks.append(delete_refresh_token(refresh_token_dto.jti, refresh_token_service))

    if access_token_jti:
        tasks.append(blacklist_token(access_token_jti, blacklisted_token_service))

    await asyncio.gather(*tasks)
