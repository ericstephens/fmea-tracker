"""
Enforce FK on fmeas.supersedes_fmea_id with ON DELETE SET NULL

Revision ID: 0007
Revises: 0006
Create Date: 2025-08-08
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # Guard: ensure table and column exist
    table_exists = bind.execute(
        sa.text(
            """
SELECT EXISTS (
  SELECT 1 FROM information_schema.tables
  WHERE table_schema = current_schema() AND table_name = 'fmeas'
)
"""
        )
    ).scalar_one()
    if not table_exists:
        return

    col_exists = bind.execute(
        sa.text(
            """
SELECT EXISTS (
  SELECT 1 FROM information_schema.columns
  WHERE table_schema = current_schema()
    AND table_name = 'fmeas'
    AND column_name = 'supersedes_fmea_id'
)
"""
        )
    ).scalar_one()
    if not col_exists:
        return

    # Check if any FK exists on the column
    has_fk = bind.execute(
        sa.text(
            """
SELECT EXISTS (
  SELECT 1
  FROM pg_constraint c
  JOIN pg_class t ON t.oid = c.conrelid
  JOIN pg_namespace n ON n.oid = t.relnamespace
  WHERE n.nspname = current_schema()
    AND t.relname = 'fmeas'
    AND c.contype = 'f'
    AND pg_get_constraintdef(c.oid) LIKE 'FOREIGN KEY (supersedes_fmea_id)%'
);
"""
        )
    ).scalar_one()

    if not has_fk:
        op.create_foreign_key(
            "fk_fmeas_supersedes_fmea_id_fmeas",
            "fmeas",
            "fmeas",
            ["supersedes_fmea_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    # Best-effort drop of the created FK
    try:
        op.drop_constraint("fk_fmeas_supersedes_fmea_id_fmeas", "fmeas", type_="foreignkey")
    except Exception:
        pass
