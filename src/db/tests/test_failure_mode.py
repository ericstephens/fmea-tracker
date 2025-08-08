from __future__ import annotations

from sqlalchemy import select

from db.models import FailureMode


def test_insert_and_query_failure_mode(db_session):
    fm = FailureMode(name="Overheating", severity=9)
    db_session.add(fm)
    db_session.flush()  # get id without commit

    # Query back
    stmt = select(FailureMode).where(FailureMode.name == "Overheating")
    result = db_session.execute(stmt).scalar_one()

    assert result.id is not None
    assert result.name == "Overheating"
    assert result.severity == 9
