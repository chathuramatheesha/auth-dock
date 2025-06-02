from enum import Enum


class TokenType(str, Enum):
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    EMAIL_TOKEN = "email_token"
