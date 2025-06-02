from enum import Enum


class TokenType(str, Enum):
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    EMAIL_TOKEN = "email_token"


class BlacklistReason(str, Enum):
    LOGOUT = "logout"
    PASSWORD_CHANGED = "password_changed"
    TOKEN_ROTATION = "token_rotation"
    ACCOUNT_DEACTIVATED = "account_deactivated"
    ACCOUNT_SUSPENDED = "account_suspended"
    ADMIN_REVOKED = "admin_revoked"
    COMPROMISED_TOKEN = "compromised_token"
