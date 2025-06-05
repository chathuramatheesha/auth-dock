from app.core import ULID
from ..constants import token_constants


class JWTTokenCredentialsInvalidError(Exception):
    def __init__(self, err: str = token_constants.JWT_CREDENTIALS_INVALID):
        super().__init__(err)


class JWTTokenInvalidError(Exception):
    def __init__(self, err: str = token_constants.JWT_TOKEN_INVALID):
        super().__init__(err)


class JWTTokenExpiredError(Exception):
    def __init__(self, err: str = token_constants.JWT_TOKEN_EXPIRED):
        super().__init__(err)


class JWTTokenTypeInvalidError(Exception):
    def __init__(self, token_type: str, valid_type_list: list[str]):
        self.token_type = token_type
        self.valid_type_list = valid_type_list
        super().__init__(
            f"Invalid token type: {token_type}'. Allowed types are: {', '.join(valid_type_list)}."
        )


class BlacklistedTokenNotFoundError(Exception):
    def __init__(self, jti: ULID):
        super().__init__(f"jti with {jti} Blacklisted token not found.")


class RefreshTokenSaveFailedError(Exception):
    def __init__(self):
        super().__init__(token_constants.REFRESH_TOKEN_SAVE_FAILED_ERROR)


class RefreshTokenNotFoundError(Exception):
    def __init__(self, jti: ULID):
        self.jti = jti
        super().__init__(token_constants.REFRESH_TOKEN_NOT_FOUND)
