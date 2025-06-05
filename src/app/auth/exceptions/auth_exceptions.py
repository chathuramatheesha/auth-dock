from app.auth.constants import auth_constants


class AuthInvalidCredentialsError(Exception):
    def __init__(self, err: str = auth_constants.ERR_INVALID_CREDENTIALS):
        super().__init__(err)


class AuthAccountDeactivatedError(Exception):
    def __init__(self, err: str = auth_constants.ERR_ACCOUNT_DEACTIVATED):
        super().__init__(err)


class AuthAccountDeletedError(Exception):
    def __init__(self, err: str = auth_constants.ERR_ACCOUNT_DELETED):
        super().__init__(err)


class AuthTokenInvalidError(Exception):
    def __init__(self, err: str = auth_constants.ERR_INVALID_TOKEN):
        super().__init__(err)


class AuthTokenTypeInvalidError(Exception):
    def __init__(self, token_type: str, valid_type_list: list):
        self.token_type = token_type
        self.valid_type_list = valid_type_list
        super().__init__(
            f"Invalid token type: {token_type}'. Allowed types are: {', '.join(valid_type_list)}"
        )


class AuthTokenRevokedError(Exception):
    def __init__(self, token_type: str, revoked_reason: str):
        self.token_type = token_type
        self.revoked_reason = revoked_reason
        super().__init__(auth_constants.ERR_TOKEN_REVOKED.format(reason=revoked_reason))
