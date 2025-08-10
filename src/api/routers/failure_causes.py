from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud

router = APIRouter(prefix="/failure-causes", tags=["failure_causes"])


@router.post("/", response_model=schemas.FailureCause)
def create_failure_cause(
    cause: schemas.FailureCauseCreate,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.create_failure_cause(db=db, cause=cause)


@router.put("/{cause_id}", response_model=schemas.FailureCause)
def update_failure_cause(
    cause_id: int,
    cause_update: schemas.FailureCauseUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    db_cause = crud.update_failure_cause(db, cause_id=cause_id, cause_update=cause_update)
    if db_cause is None:
        raise HTTPException(status_code=404, detail="Failure cause not found")
    return db_cause


@router.delete("/{cause_id}")
def delete_failure_cause(
    cause_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    success = crud.delete_failure_cause(db, cause_id=cause_id)
    if not success:
        raise HTTPException(status_code=404, detail="Failure cause not found")
    return {"message": "Failure cause deleted successfully"}


@router.get("/by-failure-mode/{failure_mode_id}", response_model=list[schemas.FailureCause])
def read_causes_by_failure_mode(
    failure_mode_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.get_causes_by_failure_mode(db, failure_mode_id=failure_mode_id)