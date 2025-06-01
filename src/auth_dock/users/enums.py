from enum import Enum


class UserRole(str, Enum):
    GUEST = "guest"
    USER = "user"
    REGULAR = "regular"
    MODERATOR = "moderator"
    STAFF = "staff"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
