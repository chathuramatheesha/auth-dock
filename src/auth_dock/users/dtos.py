from dataclasses import dataclass
from datetime import datetime

from auth_dock.core import ULID
from .enums import UserRole


@dataclass(frozen=True)
class UserOutDTO:
    id: ULID
    fullname: str
    email: str
    role: UserRole
    hashed_password: str
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None
    last_login_at: datetime | None = None


@dataclass
class UserCreateDTO:
    id: ULID
    fullname: str
    email: str
    hashed_password: str
    role: UserRole
    created_at: datetime


@dataclass
class UserUpdateDTO:
    fullname: str | None = None
    email: str | None = None
    hashed_password: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    is_deleted: bool | None = None
    updated_at: datetime | None = None
    last_login_at: datetime | None = None


@dataclass
class UserCreateInDTO:
    fullname: str
    email: str
    password: str


@dataclass(frozen=True)
class UserPublicOutDTO:
    fullname: str
    email: str
    created_at: datetime
    role: UserRole
