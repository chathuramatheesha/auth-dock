from dataclasses import dataclass


@dataclass
class UserRegisterDTO:
    fullname: str | None = None
    email: str | None = None
    password: str | None = None


@dataclass
class AuthLoginOutDTO:
    access_token: str
    refresh_token: str
    token_type: str
