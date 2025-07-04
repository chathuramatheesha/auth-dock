"""Initialize Tables

Revision ID: 035585ae752a
Revises:
Create Date: 2025-06-03 06:58:53.097830

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core import ULIDTypeDB

# revision identifiers, used by Alembic.
revision: str = "035585ae752a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "blacklisted_tokens",
        sa.Column("jti", ULIDTypeDB(length=26), nullable=False),
        sa.Column(
            "reason",
            sa.Enum(
                "LOGOUT",
                "PASSWORD_CHANGED",
                "TOKEN_ROTATION",
                "ACCOUNT_DEACTIVATED",
                "ACCOUNT_SUSPENDED",
                "ADMIN_REVOKED",
                "COMPROMISED_TOKEN",
                name="blacklistreason",
            ),
            nullable=True,
        ),
        sa.Column("blacklisted_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("jti", name=op.f("pk_blacklisted_tokens")),
    )
    op.create_index(
        op.f("ix_blacklisted_tokens_jti"), "blacklisted_tokens", ["jti"], unique=False
    )
    op.create_index(
        op.f("ix_blacklisted_tokens_reason"),
        "blacklisted_tokens",
        ["reason"],
        unique=False,
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("jti", ULIDTypeDB(length=26), nullable=False),
        sa.Column("user_id", ULIDTypeDB(length=26), nullable=False),
        sa.Column("hashed_token", sa.String(length=110), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("device_info", sa.TEXT(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("jti", name=op.f("pk_refresh_tokens")),
    )
    op.create_index(
        op.f("ix_refresh_tokens_jti"), "refresh_tokens", ["jti"], unique=False
    )
    op.create_index(
        op.f("ix_refresh_tokens_user_id"), "refresh_tokens", ["user_id"], unique=False
    )
    op.create_table(
        "users",
        sa.Column("id", ULIDTypeDB(length=26), nullable=False),
        sa.Column("fullname", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("hashed_password", sa.String(length=110), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "GUEST",
                "USER",
                "REGULAR",
                "MODERATOR",
                "STAFF",
                "ADMIN",
                "SUPERADMIN",
                name="userrole",
            ),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_fullname"), "users", ["fullname"], unique=False)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_fullname"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_jti"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index(op.f("ix_blacklisted_tokens_reason"), table_name="blacklisted_tokens")
    op.drop_index(op.f("ix_blacklisted_tokens_jti"), table_name="blacklisted_tokens")
    op.drop_table("blacklisted_tokens")
    # ### end Alembic commands ###
