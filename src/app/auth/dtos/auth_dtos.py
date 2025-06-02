from dataclasses import dataclass


@dataclass
class AuthLoginInDTO:
    email: str
    password: str


@dataclass(frozen=True)
class AuthTokensOutDTO:
    access_token: str
    refresh_token: str
    token_type: str
