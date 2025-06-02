from dataclasses import dataclass


@dataclass
class AuthLoginInDTO:
    email: str
    password: str
    ip_address: str
    previous_refresh_token: str | None = None
    device_info: str | None = None


@dataclass(frozen=True)
class AuthTokensOutDTO:
    access_token: str
    refresh_token: str
    token_type: str
