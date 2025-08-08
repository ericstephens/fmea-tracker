from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.models import FMEA, FailureMode, Action


def _mk_fm(db_session, asset_id: str = "asset-ACT", name: str = "FM-ACT") -> FailureMode:
    fmea = FMEA(asset_id=asset_id, title="FMEA for actions", version=1)
    db_session.add(fmea)
    db_session.flush()
    fm = FailureMode(fmea_id=fmea.id, name=name, severity=5)
    db_session.add(fm)
    db_session.flush()
    return fm


def test_action_defaults_and_insert(db_session):
    fm = _mk_fm(db_session)

    act = Action(failure_mode_id=fm.id, description="Add gasket", owner="Alex")
    db_session.add(act)
    db_session.flush()

    got = db_session.execute(select(Action).where(Action.id == act.id)).scalar_one()
    assert got.status == "open"
    assert got.closed_at is None
    assert got.owner == "Alex"
    assert got.failure_mode_id == fm.id


def test_action_status_constraint(db_session):
    fm = _mk_fm(db_session, asset_id="asset-ACT-2", name="FM-ACT-2")

    bad = Action(failure_mode_id=fm.id, description="Invalid status", status="bogus")
    db_session.add(bad)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_cascade_delete_from_failure_mode(db_session):
    fm = _mk_fm(db_session, asset_id="asset-ACT-3", name="FM-ACT-3")

    a1 = Action(failure_mode_id=fm.id, description="Tighten torque")
    a2 = Action(failure_mode_id=fm.id, description="Add inspection step")
    db_session.add_all([a1, a2])
    db_session.flush()

    # Delete failure mode -> actions should be deleted via ON DELETE CASCADE
    db_session.delete(fm)
    db_session.flush()

    remaining = db_session.execute(select(Action).where(Action.failure_mode_id == fm.id)).scalars().all()
    assert remaining == []
