"""add OAuth account identities

Revision ID: 6f1d2a8c4b90
Revises: 20230924_add_metrics_and_twins
"""
from alembic import op
import sqlalchemy as sa

revision = "6f1d2a8c4b90"
down_revision = "20230924_add_metrics_and_twins"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("users", "password", existing_type=sa.String(length=255), nullable=True)
    op.create_table(
        "user_auth_accounts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_user_id", sa.String(length=255), nullable=False),
        sa.Column("provider_email", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_user_auth_provider_subject"),
    )
    op.create_index("ix_user_auth_accounts_user_id", "user_auth_accounts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_auth_accounts_user_id", table_name="user_auth_accounts")
    op.drop_table("user_auth_accounts")
    op.alter_column("users", "password", existing_type=sa.String(length=255), nullable=False)
