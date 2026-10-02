"""Add prediction and simulation execution history."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20261002_history"
down_revision = "6f1d2a8c4b90"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prediction_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("infrastructure.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prediction_type", sa.String(16), nullable=False),
        sa.Column("predicted_value", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("failure_probability", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(16), nullable=False),
        sa.Column("factors", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("recommended_action", sa.String(1000), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("horizon_minutes", sa.Integer(), nullable=False),
        sa.Column("historical_metrics", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("model_metrics", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("prediction_source", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_prediction_history_service_id", "prediction_history", ["service_id"])
    op.create_index("ix_prediction_history_created_at", "prediction_history", ["created_at"])
    op.create_table(
        "simulation_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("infrastructure.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scenario", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("baseline_state", postgresql.JSONB(), nullable=False),
        sa.Column("scenario_changes", postgresql.JSONB(), nullable=False),
        sa.Column("simulated_state", postgresql.JSONB(), nullable=False),
        sa.Column("simulated_health_score", sa.Float(), nullable=False),
        sa.Column("simulated_failure_probability", sa.Float(), nullable=False),
        sa.Column("simulated_operational_status", sa.String(32), nullable=False),
        sa.Column("impact_summary", postgresql.JSONB(), nullable=False),
        sa.Column("predicted_impact", postgresql.JSONB(), nullable=False),
        sa.Column("recommendations", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_simulation_history_service_id", "simulation_history", ["service_id"])
    op.create_index("ix_simulation_history_created_at", "simulation_history", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_simulation_history_created_at", table_name="simulation_history")
    op.drop_index("ix_simulation_history_service_id", table_name="simulation_history")
    op.drop_table("simulation_history")
    op.drop_index("ix_prediction_history_created_at", table_name="prediction_history")
    op.drop_index("ix_prediction_history_service_id", table_name="prediction_history")
    op.drop_table("prediction_history")
