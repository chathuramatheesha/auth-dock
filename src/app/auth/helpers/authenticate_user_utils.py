from app.core import ULID
from ..enums import TokenType
from ..exceptions.auth_exceptions import (
    AuthTokenTypeInvalidError,
    AuthTokenRevokedError,
)
from ..exceptions.token_exceptions import BlacklistedTokenNotFoundError
from ..services.blacklisted_token_service import BlacklistedTokenService


def validate_token_type(token_type: TokenType) -> None:
    if token_type not in TokenType:
        raise AuthTokenTypeInvalidError(
            token_type,
            [TokenType.ACCESS_TOKEN.value, TokenType.REFRESH_TOKEN.value],
        )


async def check_token_blacklist(
    token_service: BlacklistedTokenService, jti: str, token_type: TokenType
):
    try:
        blacklisted_token = await token_service.get_by_jti(ULID(jti))

        if blacklisted_token:
            raise AuthTokenRevokedError(
                token_type.value,
                blacklisted_token.reason.value,
            )

    except BlacklistedTokenNotFoundError:
        pass
