from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003"
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

    # Create failure_causes
    if "failure_causes" not in tables:
        op.create_table(
            "failure_causes",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("failure_mode_id", sa.Integer(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["failure_mode_id"], ["failure_modes.id"], name="fk_failure_causes_failure_mode_id", ondelete="CASCADE"),
        )
        op.create_index("ix_failure_causes_failure_mode_id", "failure_causes", ["failure_mode_id"]) 

    # Create failure_effects
    if "failure_effects" not in tables:
        op.create_table(
            "failure_effects",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("failure_mode_id", sa.Integer(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("level", sa.String(length=32), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["failure_mode_id"], ["failure_modes.id"], name="fk_failure_effects_failure_mode_id", ondelete="CASCADE"),
        )
        op.create_index("ix_failure_effects_failure_mode_id", "failure_effects", ["failure_mode_id"]) 
        op.create_check_constraint(
            "ck_failure_effects_level_valid",
            "failure_effects",
            "level IS NULL OR level IN ('local','next_higher','end_user')",
        )

    # Create controls
    if "controls" not in tables:
        op.create_table(
            "controls",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("failure_mode_id", sa.Integer(), nullable=False),
            sa.Column("type", sa.String(length=16), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("method_ref", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["failure_mode_id"], ["failure_modes.id"], name="fk_controls_failure_mode_id", ondelete="CASCADE"),
        )
        op.create_index("ix_controls_failure_mode_id", "controls", ["failure_mode_id"]) 
        op.create_check_constraint(
            "ck_controls_type_valid",
            "controls",
            "type IN ('prevention','detection')",
        )


def downgrade() -> None:
    # Drop in reverse order
    for name in (
        "ck_controls_type_valid",
    ):
        try:
            op.drop_constraint(name, "controls", type_="check")
        except Exception:
            pass
    try:
        op.drop_index("ix_controls_failure_mode_id", table_name="controls")
    except Exception:
        pass
    try:
        op.drop_constraint("fk_controls_failure_mode_id", "controls", type_="foreignkey")
    except Exception:
        pass
    try:
        op.drop_table("controls")
    except Exception:
        pass

    for name in (
        "ck_failure_effects_level_valid",
    ):
        try:
            op.drop_constraint(name, "failure_effects", type_="check")
        except Exception:
            pass
    try:
        op.drop_index("ix_failure_effects_failure_mode_id", table_name="failure_effects")
    except Exception:
        pass
    try:
        op.drop_constraint("fk_failure_effects_failure_mode_id", "failure_effects", type_="foreignkey")
    except Exception:
        pass
    try:
        op.drop_table("failure_effects")
    except Exception:
        pass

    try:
        op.drop_index("ix_failure_causes_failure_mode_id", table_name="failure_causes")
    except Exception:
        pass
    try:
        op.drop_constraint("fk_failure_causes_failure_mode_id", "failure_causes", type_="foreignkey")
    except Exception:
        pass
    try:
        op.drop_table("failure_causes")
    except Exception:
        pass
