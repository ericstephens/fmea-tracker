from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud

router = APIRouter(prefix="/controls", tags=["controls"])


@router.post("/", response_model=schemas.Control)
def create_control(
    control: schemas.ControlCreate,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.create_control(db=db, control=control)


@router.put("/{control_id}", response_model=schemas.Control)
def update_control(
    control_id: int,
    control_update: schemas.ControlUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    db_control = crud.update_control(db, control_id=control_id, control_update=control_update)
    if db_control is None:
        raise HTTPException(status_code=404, detail="Control not found")
    return db_control


@router.delete("/{control_id}")
def delete_control(
    control_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    success = crud.delete_control(db, control_id=control_id)
    if not success:
        raise HTTPException(status_code=404, detail="Control not found")
    return {"message": "Control deleted successfully"}


@router.get("/by-failure-mode/{failure_mode_id}", response_model=list[schemas.Control])
def read_controls_by_failure_mode(
    failure_mode_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.get_controls_by_failure_mode(db, failure_mode_id=failure_mode_id)