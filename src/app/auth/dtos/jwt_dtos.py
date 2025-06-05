from dataclasses import dataclass
from datetime import datetime

from ..enums import TokenType


# TOKEN BASE
@dataclass
class _TokenBase:
    sub: str
    jti: str
    exp: datetime
    iat: datetime
    type: TokenType


# ACCESS TOKEN
@dataclass
class JWTAccessTokenDTO(_TokenBase):
    pass


# REFRESH TOKEN
@dataclass
class JWTRefreshTokenDTO(_TokenBase):
    ip: str


# EMAIL TOKEN
@dataclass
class JWTEmailTokenDTO(_TokenBase):
    pass
