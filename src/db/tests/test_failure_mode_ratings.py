from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.models import FMEA, FailureMode


def test_default_ratings_and_rpn(db_session):
    fmea = FMEA(asset_id="asset-RPN", title="Ratings FMEA", version=1)
    db_session.add(fmea)
    db_session.flush()

    fm = FailureMode(fmea_id=fmea.id, name="Leakage", severity=5)
    db_session.add(fm)
    db_session.flush()

    # Defaults: occurrence=1, detection=10, rpn=5*1*10=50
    stmt = select(FailureMode).where(FailureMode.id == fm.id)
    got = db_session.execute(stmt).scalar_one()
    assert got.occurrence == 1
    assert got.detection == 10
    assert got.rpn == 5 * 1 * 10


def test_set_ratings_and_rpn_computation(db_session):
    fmea = FMEA(asset_id="asset-RPN2", title="Ratings FMEA 2", version=1)
    db_session.add(fmea)
    db_session.flush()

    fm = FailureMode(
        fmea_id=fmea.id,
        name="Overcurrent",
        severity=7,
        occurrence=3,
        detection=4,
    )
    db_session.add(fm)
    db_session.flush()

    got = db_session.execute(select(FailureMode).where(FailureMode.id == fm.id)).scalar_one()
    assert got.rpn == 7 * 3 * 4


def test_rating_bounds_enforced(db_session):
    fmea = FMEA(asset_id="asset-RPN3", title="Ratings FMEA 3", version=1)
    db_session.add(fmea)
    db_session.flush()

    # Invalid severity (0)
    db_session.add(
        FailureMode(fmea_id=fmea.id, name="BadSeverity", severity=0, occurrence=1, detection=1)
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    # Invalid occurrence (11)
    db_session.add(
        FailureMode(fmea_id=fmea.id, name="BadOccurrence", severity=5, occurrence=11, detection=1)
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    # Invalid detection (-1)
    db_session.add(
        FailureMode(fmea_id=fmea.id, name="BadDetection", severity=5, occurrence=1, detection=-1)
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()
