from __future__ import annotations

from sqlalchemy import select

from db.models import FailureMode, FMEA


def test_insert_and_query_failure_mode(db_session):
    # Create an FMEA record to link failure modes to
    fmea = FMEA(asset_id="asset-123", title="Engine FMEA", description="Baseline", version=1)
    db_session.add(fmea)
    db_session.flush()

    fm = FailureMode(fmea_id=fmea.id, name="Overheating", severity=9)
    db_session.add(fm)
    db_session.flush()  # get id without commit

    # Query back
    stmt = select(FailureMode).where(FailureMode.name == "Overheating")
    result = db_session.execute(stmt).scalar_one()

    assert result.id is not None
    assert result.fmea_id == fmea.id
    assert result.name == "Overheating"
    assert result.severity == 9
