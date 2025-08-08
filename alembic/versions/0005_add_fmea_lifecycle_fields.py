from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(inspector, name: str) -> bool:
    try:
        return name in inspector.get_table_names()
    except Exception:
        return False


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Ensure fmeas exists (pristine DB safety)
    if not _table_exists(inspector, "fmeas"):
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

    # Add lifecycle columns if missing
    with op.batch_alter_table("fmeas") as batch_op:
        inspector = inspect(bind)
        cols = {c["name"] for c in inspector.get_columns("fmeas")}
        if "status" not in cols:
            batch_op.add_column(sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"))
        if "approved_by" not in cols:
            batch_op.add_column(sa.Column("approved_by", sa.String(length=255), nullable=True))
        if "approved_at" not in cols:
            batch_op.add_column(sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
        if "effective_date" not in cols:
            batch_op.add_column(sa.Column("effective_date", sa.DateTime(timezone=True), nullable=True))
        if "created_by" not in cols:
            batch_op.add_column(sa.Column("created_by", sa.String(length=255), nullable=True))
        if "updated_by" not in cols:
            batch_op.add_column(sa.Column("updated_by", sa.String(length=255), nullable=True))
        if "supersedes_fmea_id" not in cols:
            batch_op.add_column(sa.Column("supersedes_fmea_id", sa.Integer(), nullable=True))

    # Create index and FK and check constraint idempotently
    # Index
    try:
        op.create_index("ix_fmeas_supersedes_fmea_id", "fmeas", ["supersedes_fmea_id"])
    except Exception:
        pass
    # FK
    try:
        op.create_foreign_key(
            "fk_fmeas_supersedes_fmea_id_fmeas",
            "fmeas",
            "fmeas",
            ["supersedes_fmea_id"],
            ["id"],
            ondelete="SET NULL",
        )
    except Exception:
        pass
    # Check constraint for status
    try:
        op.create_check_constraint(
            "ck_fmeas_status_valid",
            "fmeas",
            "status IN ('draft','review','approved','superseded')",
        )
    except Exception:
        pass

    # Drop server_default for status to avoid unintended defaults in app logic
    try:
        op.alter_column("fmeas", "status", server_default=None)
    except Exception:
        pass


def downgrade() -> None:
    # Best-effort cleanup
    try:
        op.alter_column("fmeas", "status", server_default=None)
    except Exception:
        pass
    for name in (
        "ck_fmeas_status_valid",
        "fk_fmeas_supersedes_fmea_id_fmeas",
    ):
        try:
            if name.startswith("ck_"):
                op.drop_constraint(name, "fmeas", type_="check")
            else:
                op.drop_constraint(name, "fmeas", type_="foreignkey")
        except Exception:
            pass
    try:
        op.drop_index("ix_fmeas_supersedes_fmea_id", table_name="fmeas")
    except Exception:
        pass
    with op.batch_alter_table("fmeas") as batch_op:
        for col in (
            "supersedes_fmea_id",
            "updated_by",
            "created_by",
            "effective_date",
            "approved_at",
            "approved_by",
            "status",
        ):
            try:
                batch_op.drop_column(col)
            except Exception:
                pass
