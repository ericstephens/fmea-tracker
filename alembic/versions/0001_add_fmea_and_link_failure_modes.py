from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(conn, name: str) -> bool:
    inspector = inspect(conn)
    return name in inspector.get_table_names()


def column_exists(conn, table: str, column: str) -> bool:
    inspector = inspect(conn)
    return any(col["name"] == column for col in inspector.get_columns(table))


def constraint_exists(conn, table: str, constraint_name: str) -> bool:
    inspector = inspect(conn)
    for uc in inspector.get_unique_constraints(table):
        if uc.get("name") == constraint_name:
            return True
    for fk in inspector.get_foreign_keys(table):
        if fk.get("name") == constraint_name:
            return True
    for pk in inspector.get_pk_constraint(table) or []:
        if isinstance(pk, dict) and pk.get("name") == constraint_name:
            return True
    return False


def upgrade() -> None:
    bind = op.get_bind()

    # Create fmeas table if not present
    if not table_exists(bind, "fmeas"):
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

    # Ensure failure_modes table has required columns/constraints
    if table_exists(bind, "failure_modes"):
        # add fmea_id if missing
        if not column_exists(bind, "failure_modes", "fmea_id"):
            op.add_column("failure_modes", sa.Column("fmea_id", sa.Integer(), nullable=True))
            # index
            op.create_index("ix_failure_modes_fmea_id", "failure_modes", ["fmea_id"])
            # FK to fmeas.id (defer NOT NULL until after potential backfill)
            op.create_foreign_key(
                "fk_failure_modes_fmea_id_fmeas",
                source_table="failure_modes",
                referent_table="fmeas",
                local_cols=["fmea_id"],
                remote_cols=["id"],
                ondelete="CASCADE",
            )
        # drop unique on name if it exists under a known default name
        # Common default name in Postgres is "failure_modes_name_key"
        try:
            if constraint_exists(bind, "failure_modes", "failure_modes_name_key"):
                op.drop_constraint("failure_modes_name_key", "failure_modes", type_="unique")
        except Exception:
            pass
        # create unique (fmea_id, name) if not present
        if not constraint_exists(bind, "failure_modes", "uq_failure_mode_fmea_name"):
            op.create_unique_constraint(
                "uq_failure_mode_fmea_name", "failure_modes", ["fmea_id", "name"]
            )
        # Make fmea_id NOT NULL if table is empty or if you know it's safe.
        # For initial dev DBs this should be safe.
        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM failure_modes LIMIT 1) THEN
                    ALTER TABLE failure_modes ALTER COLUMN fmea_id SET NOT NULL;
                END IF;
            END$$;
            """
        )
    else:
        # Create fresh failure_modes with new schema
        op.create_table(
            "failure_modes",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("fmea_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("severity", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["fmea_id"], ["fmeas.id"], name="fk_failure_modes_fmea_id_fmeas", ondelete="CASCADE"),
            sa.UniqueConstraint("fmea_id", "name", name="uq_failure_mode_fmea_name"),
        )
        op.create_index("ix_failure_modes_fmea_id", "failure_modes", ["fmea_id"]) 


def downgrade() -> None:
    bind = op.get_bind()
    if table_exists(bind, "failure_modes"):
        try:
            op.drop_constraint("uq_failure_mode_fmea_name", "failure_modes", type_="unique")
        except Exception:
            pass
        try:
            op.drop_constraint("fk_failure_modes_fmea_id_fmeas", "failure_modes", type_="foreignkey")
        except Exception:
            pass
        try:
            op.drop_index("ix_failure_modes_fmea_id", table_name="failure_modes")
        except Exception:
            pass
        if column_exists(bind, "failure_modes", "fmea_id"):
            try:
                op.drop_column("failure_modes", "fmea_id")
            except Exception:
                pass
    if table_exists(bind, "fmeas"):
        try:
            op.drop_index("ix_fmeas_asset_id", table_name="fmeas")
        except Exception:
            pass
        try:
            op.drop_constraint("uq_fmea_asset_version", "fmeas", type_="unique")
        except Exception:
            pass
        try:
            op.drop_table("fmeas")
        except Exception:
            pass
