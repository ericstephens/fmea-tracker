from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud

router = APIRouter(prefix="/failure-modes", tags=["failure_modes"])


@router.post("/", response_model=schemas.FailureMode)
def create_failure_mode(
    failure_mode: schemas.FailureModeCreate,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.create_failure_mode(db=db, failure_mode=failure_mode)


@router.get("/{failure_mode_id}", response_model=schemas.FailureMode)
def read_failure_mode(
    failure_mode_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    db_failure_mode = crud.get_failure_mode(db, failure_mode_id=failure_mode_id)
    if db_failure_mode is None:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    return db_failure_mode


@router.put("/{failure_mode_id}", response_model=schemas.FailureMode)
def update_failure_mode(
    failure_mode_id: int,
    failure_mode_update: schemas.FailureModeUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    db_failure_mode = crud.update_failure_mode(db, failure_mode_id=failure_mode_id, failure_mode_update=failure_mode_update)
    if db_failure_mode is None:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    return db_failure_mode


@router.delete("/{failure_mode_id}")
def delete_failure_mode(
    failure_mode_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    success = crud.delete_failure_mode(db, failure_mode_id=failure_mode_id)
    if not success:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    return {"message": "Failure mode deleted successfully"}


@router.get("/by-fmea/{fmea_id}", response_model=list[schemas.FailureMode])
def read_failure_modes_by_fmea(
    fmea_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.get_failure_modes_by_fmea(db, fmea_id=fmea_id)