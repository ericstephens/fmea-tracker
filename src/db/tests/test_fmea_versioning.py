from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.models import FMEA, FailureMode


def test_fmea_version_uniqueness(db_session):
    # Two FMEA records for the same asset with different versions are allowed
    fmea_v1 = FMEA(asset_id="asset-123", title="Engine FMEA v1", version=1)
    fmea_v2 = FMEA(asset_id="asset-123", title="Engine FMEA v2", version=2)
    db_session.add_all([fmea_v1, fmea_v2])
    db_session.flush()
    # Persist the valid rows so subsequent rollback doesn't remove them
    db_session.commit()

    # Attempt to insert a duplicate version for the same asset should fail
    dup = FMEA(asset_id="asset-123", title="Duplicate v1", version=1)
    db_session.add(dup)
    with pytest.raises(IntegrityError):
        db_session.flush()
    # Reset failed transaction state before proceeding
    db_session.rollback()

    # But same version for different asset is fine (fresh insert after rollback)
    other = FMEA(asset_id="asset-999", title="Other asset v1", version=1)
    db_session.add(other)
    db_session.flush()

    rows = db_session.execute(select(FMEA).where(FMEA.asset_id == "asset-123")).scalars().all()
    assert len(rows) == 2


def test_failure_mode_unique_per_fmea(db_session):
    # Set up two versions for the same asset
    fmea1 = FMEA(asset_id="asset-A", title="A v1", version=1)
    fmea2 = FMEA(asset_id="asset-A", title="A v2", version=2)
    db_session.add_all([fmea1, fmea2])
    db_session.flush()

    # Insert a failure mode under v1
    fm1 = FailureMode(fmea_id=fmea1.id, name="Overheating", severity=9)
    db_session.add(fm1)
    db_session.flush()

    # Duplicate name under the same FMEA should violate unique constraint
    db_session.add(FailureMode(fmea_id=fmea1.id, name="Overheating", severity=5))
    with pytest.raises(IntegrityError):
        db_session.flush()
    # Reset failed transaction state before proceeding
    db_session.rollback()

    # Recreate the second FMEA version after rollback
    fmea2 = FMEA(asset_id="asset-A", title="A v2", version=2)
    db_session.add(fmea2)
    db_session.flush()

    # Same name but under different FMEA (version) should be allowed
    db_session.add(FailureMode(fmea_id=fmea2.id, name="Overheating", severity=4))
    db_session.flush()
