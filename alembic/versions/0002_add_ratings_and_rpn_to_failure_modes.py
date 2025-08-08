from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    # Ensure fmeas table exists (in case DB is pristine or was reset)
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
        # Create table with full schema (in case 0001 ran on a pristine DB without creating it)
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
        # Add range constraints
        op.create_check_constraint(
            "ck_failure_modes_severity_range",
            "failure_modes",
            "severity BETWEEN 1 AND 10",
        )
        op.create_check_constraint(
            "ck_failure_modes_occurrence_range",
            "failure_modes",
            "occurrence BETWEEN 1 AND 10",
        )
        op.create_check_constraint(
            "ck_failure_modes_detection_range",
            "failure_modes",
            "detection BETWEEN 1 AND 10",
        )
        # Remove server defaults for occurrence/detection to match ORM (keep NOT NULL)
        op.alter_column("failure_modes", "occurrence", server_default=None)
        op.alter_column("failure_modes", "detection", server_default=None)
    else:
        # Table exists: add columns, constraints
        op.add_column(
            "failure_modes",
            sa.Column("occurrence", sa.Integer(), nullable=False, server_default=sa.text("1")),
        )
        op.add_column(
            "failure_modes",
            sa.Column("detection", sa.Integer(), nullable=False, server_default=sa.text("10")),
        )
        op.add_column(
            "failure_modes",
            sa.Column(
                "rpn",
                sa.Integer(),
                sa.Computed("(severity * occurrence * detection)", persisted=True),
                nullable=False,
            ),
        )
        op.create_check_constraint(
            "ck_failure_modes_severity_range",
            "failure_modes",
            "severity BETWEEN 1 AND 10",
        )
        op.create_check_constraint(
            "ck_failure_modes_occurrence_range",
            "failure_modes",
            "occurrence BETWEEN 1 AND 10",
        )
        op.create_check_constraint(
            "ck_failure_modes_detection_range",
            "failure_modes",
            "detection BETWEEN 1 AND 10",
        )
        op.alter_column("failure_modes", "occurrence", server_default=None)
        op.alter_column("failure_modes", "detection", server_default=None)


def downgrade() -> None:
    # Drop constraints
    try:
        op.drop_constraint("ck_failure_modes_detection_range", "failure_modes", type_="check")
    except Exception:
        pass
    try:
        op.drop_constraint("ck_failure_modes_occurrence_range", "failure_modes", type_="check")
    except Exception:
        pass
    try:
        op.drop_constraint("ck_failure_modes_severity_range", "failure_modes", type_="check")
    except Exception:
        pass
    # Drop columns (computed first is fine)
    try:
        op.drop_column("failure_modes", "rpn")
    except Exception:
        pass
    try:
        op.drop_column("failure_modes", "detection")
    except Exception:
        pass
    try:
        op.drop_column("failure_modes", "occurrence")
    except Exception:
        pass
