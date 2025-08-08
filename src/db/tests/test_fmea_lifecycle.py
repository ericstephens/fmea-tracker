from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.models import FMEA


def test_fmea_lifecycle_defaults_and_insert(db_session):
    f = FMEA(asset_id="A-100", title="Pump FMEA", version=1)
    db_session.add(f)
    db_session.flush()

    got = db_session.execute(select(FMEA).where(FMEA.id == f.id)).scalar_one()
    assert got.status == "draft"
    assert got.approved_by is None
    assert got.approved_at is None
    assert got.effective_date is None
    assert got.created_by is None
    assert got.updated_by is None
    assert got.supersedes_fmea_id is None


def test_fmea_status_constraint(db_session):
    f = FMEA(asset_id="A-101", title="Valve FMEA", version=1, status="draft")
    db_session.add(f)
    db_session.flush()

    f.status = "approved"
    db_session.flush()

    f.status = "not_a_status"
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_fmea_supersedes_link_and_ondelete_set_null(db_session):
    # Create prior and superseding FMEA
    prior = FMEA(asset_id="A-102", title="Motor FMEA v1", version=1, status="approved")
    db_session.add(prior)
    db_session.flush()

    superseding = FMEA(
        asset_id="A-102",
        title="Motor FMEA v2",
        version=2,
        status="review",
        supersedes_fmea_id=prior.id,
        approved_by=None,
    )
    db_session.add(superseding)
    db_session.flush()

    got = db_session.execute(select(FMEA).where(FMEA.id == superseding.id)).scalar_one()
    assert got.supersedes_fmea_id == prior.id

    # Delete prior; superseding should set FK to NULL due to ondelete=SET NULL
    db_session.delete(prior)
    db_session.commit()  # Commit to trigger FK constraint action

    # Refresh the superseding object to get updated state from DB
    db_session.refresh(superseding)
    assert superseding.supersedes_fmea_id is None
    
    # Also verify with a fresh query
    got2 = db_session.execute(select(FMEA).where(FMEA.id == superseding.id)).scalar_one()
    assert got2.supersedes_fmea_id is None


def test_fmea_approval_fields(db_session):
    f = FMEA(asset_id="A-103", title="Gearbox FMEA", version=1)
    db_session.add(f)
    db_session.flush()

    # Set approval and effective dates
    now = datetime.now(timezone.utc)
    eff = now + timedelta(days=7)
    f.status = "approved"
    f.approved_by = "qa.manager@example.com"
    f.approved_at = now
    f.effective_date = eff
    f.created_by = "author@example.com"
    f.updated_by = "author@example.com"
    db_session.flush()

    got = db_session.execute(select(FMEA).where(FMEA.id == f.id)).scalar_one()
    assert got.status == "approved"
    assert got.approved_by and got.approved_at and got.effective_date
