from datetime import datetime, timezone

from sqlalchemy import String, TEXT, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core import ULID, ULIDTypeDB
from app.db import Base
from .enums import BlacklistReason


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    jti: Mapped[ULID] = mapped_column(ULIDTypeDB, primary_key=True, index=True)
    user_id: Mapped[ULID] = mapped_column(ULIDTypeDB, nullable=False, index=True)
    hashed_token: Mapped[str] = mapped_column(String(110), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    device_info: Mapped[str] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    jti: Mapped[ULID] = mapped_column(ULIDTypeDB, primary_key=True, index=True)
    reason: Mapped[BlacklistReason] = mapped_column(
        Enum(BlacklistReason), nullable=True, index=True
    )
    blacklisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
