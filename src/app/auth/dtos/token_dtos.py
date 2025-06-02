from dataclasses import dataclass
from datetime import datetime

from app.core import ULID


@dataclass
class RefreshTokenDTO:
    jti: ULID
    user_id: ULID
    hashed_token: str
    ip_address: str
    created_at: datetime
    expires_at: datetime
    device_info: str | None = None
