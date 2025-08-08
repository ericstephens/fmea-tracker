from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

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

    # Find any existing FK constraints on supersedes_fmea_id
    existing = bind.execute(
        sa.text(
            """
SELECT c.conname
FROM pg_constraint c
JOIN pg_class t ON t.oid = c.conrelid
JOIN pg_namespace n ON n.oid = t.relnamespace
WHERE n.nspname = current_schema()
  AND t.relname = 'fmeas'
  AND c.contype = 'f'
  AND pg_get_constraintdef(c.oid) LIKE 'FOREIGN KEY (supersedes_fmea_id)%'
"""
        )
    ).scalars().all()

    # Drop only constraints that actually exist
    for name in existing:
        op.drop_constraint(name, "fmeas", type_="foreignkey")

    # If no FK now exists on supersedes_fmea_id, create the desired one
    still_exists = bind.execute(
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

    if not still_exists:
        op.create_foreign_key(
            "fk_fmeas_supersedes_fmea_id_fmeas",
            "fmeas",
            "fmeas",
            ["supersedes_fmea_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    # Best-effort: drop our named FK; leave default system FK (if any) untouched
    try:
        op.drop_constraint("fk_fmeas_supersedes_fmea_id_fmeas", "fmeas", type_="foreignkey")
    except Exception:
        pass
