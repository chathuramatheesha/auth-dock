from dataclasses import dataclass


@dataclass
class AuthLoginInDTO:
    email: str
    password: str
    ip_address: str
    previous_access_token: str | None = None
    previous_refresh_token: str | None = None
    device_info: str | None = None


@dataclass(frozen=True)
class AuthTokensOutDTO:
    access_token: str
    refresh_token: str | None
    token_type: str


@dataclass
class RefreshAccessTokenInDTO:
    access_token: str
    refresh_token: str
    ip_address: str
    device_info: str
