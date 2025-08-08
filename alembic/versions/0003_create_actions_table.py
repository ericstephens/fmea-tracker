from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    # Ensure dependencies exist
    if "fmeas" not in tables:
        op.create_table(
            "fmeas",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("asset_id", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.UniqueConstraint("asset_id", "version", name="uq_fmea_asset_version"),
        )
        op.create_index("ix_fmeas_asset_id", "fmeas", ["asset_id"]) 

    if "failure_modes" not in tables:
        op.create_table(
            "failure_modes",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("fmea_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("severity", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("occurrence", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("detection", sa.Integer(), nullable=False, server_default=sa.text("10")),
            sa.Column(
                "rpn",
                sa.Integer(),
                sa.Computed("(severity * occurrence * detection)", persisted=True),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["fmea_id"], ["fmeas.id"], name="fk_failure_modes_fmea_id_fmeas", ondelete="CASCADE"),
            sa.UniqueConstraint("fmea_id", "name", name="uq_failure_mode_fmea_name"),
        )
        op.create_index("ix_failure_modes_fmea_id", "failure_modes", ["fmea_id"]) 
        op.create_check_constraint("ck_failure_modes_severity_range", "failure_modes", "severity BETWEEN 1 AND 10")
        op.create_check_constraint("ck_failure_modes_occurrence_range", "failure_modes", "occurrence BETWEEN 1 AND 10")
        op.create_check_constraint("ck_failure_modes_detection_range", "failure_modes", "detection BETWEEN 1 AND 10")
        op.alter_column("failure_modes", "occurrence", server_default=None)
        op.alter_column("failure_modes", "detection", server_default=None)

    # Create actions table if not exists
    if "actions" not in tables:
        op.create_table(
            "actions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("failure_mode_id", sa.Integer(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("owner", sa.String(length=255), nullable=True),
            sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'open'")),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["failure_mode_id"], ["failure_modes.id"], name="fk_actions_failure_mode_id", ondelete="CASCADE"),
        )
        op.create_index("ix_actions_failure_mode_id", "actions", ["failure_mode_id"]) 
        op.create_check_constraint(
            "ck_actions_status_valid",
            "actions",
            "status IN ('open','in_progress','closed','deferred')",
        )


def downgrade() -> None:
    # Drop actions
    try:
        op.drop_constraint("ck_actions_status_valid", "actions", type_="check")
    except Exception:
        pass
    try:
        op.drop_index("ix_actions_failure_mode_id", table_name="actions")
    except Exception:
        pass
    try:
        op.drop_constraint("fk_actions_failure_mode_id", "actions", type_="foreignkey")
    except Exception:
        pass
    try:
        op.drop_table("actions")
    except Exception:
        pass
