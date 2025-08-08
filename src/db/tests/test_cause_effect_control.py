from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.models import FMEA, FailureMode, FailureCause, FailureEffect, Control


def _mk_fm(db_session, asset_id: str = "asset-CEC", name: str = "FM-CEC") -> FailureMode:
    fmea = FMEA(asset_id=asset_id, title="FMEA for CEC", version=1)
    db_session.add(fmea)
    db_session.flush()
    fm = FailureMode(fmea_id=fmea.id, name=name, severity=5)
    db_session.add(fm)
    db_session.flush()
    return fm


def test_insert_cause_effect_control_and_query(db_session):
    fm = _mk_fm(db_session)

    cause = FailureCause(failure_mode_id=fm.id, description="Poor sealing surface")
    effect = FailureEffect(failure_mode_id=fm.id, description="Leak to environment", level="end_user")
    ctrl_prev = Control(failure_mode_id=fm.id, type="prevention", description="Add surface finish spec")
    ctrl_det = Control(failure_mode_id=fm.id, type="detection", description="Helium leak test")

    db_session.add_all([cause, effect, ctrl_prev, ctrl_det])
    db_session.flush()

    got_cause = db_session.execute(select(FailureCause).where(FailureCause.id == cause.id)).scalar_one()
    got_effect = db_session.execute(select(FailureEffect).where(FailureEffect.id == effect.id)).scalar_one()
    got_ctrls = db_session.execute(select(Control).where(Control.failure_mode_id == fm.id)).scalars().all()

    assert got_cause.description.startswith("Poor")
    assert got_effect.level == "end_user"
    assert {c.type for c in got_ctrls} == {"prevention", "detection"}


def test_effect_level_constraint(db_session):
    fm = _mk_fm(db_session, asset_id="asset-CEC2", name="FM-CEC2")

    bad_effect = FailureEffect(failure_mode_id=fm.id, description="Bad", level="system")
    db_session.add(bad_effect)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_controls_type_constraint(db_session):
    fm = _mk_fm(db_session, asset_id="asset-CEC3", name="FM-CEC3")

    bad_ctrl = Control(failure_mode_id=fm.id, type="other", description="Nope")
    db_session.add(bad_ctrl)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_cascade_delete(db_session):
    fm = _mk_fm(db_session, asset_id="asset-CEC4", name="FM-CEC4")

    db_session.add(FailureCause(failure_mode_id=fm.id, description="Root cause"))
    db_session.add(FailureEffect(failure_mode_id=fm.id, description="Effect", level="local"))
    db_session.add(Control(failure_mode_id=fm.id, type="prevention", description="Control"))
    db_session.flush()

    db_session.delete(fm)
    db_session.flush()

    # All children should be gone
    assert db_session.execute(select(FailureCause).where(FailureCause.failure_mode_id == fm.id)).first() is None
    assert db_session.execute(select(FailureEffect).where(FailureEffect.failure_mode_id == fm.id)).first() is None
    assert db_session.execute(select(Control).where(Control.failure_mode_id == fm.id)).first() is None
