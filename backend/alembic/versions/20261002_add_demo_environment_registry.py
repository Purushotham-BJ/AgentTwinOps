"""Add shared demo environment registry."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20261002_demo_environment"
down_revision = "20261002_history"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "demo_environments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("seed_key", sa.String(100), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ready"),
        sa.Column(
            "initialized_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("seed_key", name="uq_demo_environments_seed_key"),
    )
    op.create_index("ix_demo_environments_seed_key", "demo_environments", ["seed_key"])


def downgrade() -> None:
    op.drop_index("ix_demo_environments_seed_key", table_name="demo_environments")
    op.drop_table("demo_environments")
