from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud

router = APIRouter(prefix="/failure-effects", tags=["failure_effects"])


@router.post("/", response_model=schemas.FailureEffect)
def create_failure_effect(
    effect: schemas.FailureEffectCreate,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.create_failure_effect(db=db, effect=effect)


@router.put("/{effect_id}", response_model=schemas.FailureEffect)
def update_failure_effect(
    effect_id: int,
    effect_update: schemas.FailureEffectUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    db_effect = crud.update_failure_effect(db, effect_id=effect_id, effect_update=effect_update)
    if db_effect is None:
        raise HTTPException(status_code=404, detail="Failure effect not found")
    return db_effect


@router.delete("/{effect_id}")
def delete_failure_effect(
    effect_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    success = crud.delete_failure_effect(db, effect_id=effect_id)
    if not success:
        raise HTTPException(status_code=404, detail="Failure effect not found")
    return {"message": "Failure effect deleted successfully"}


@router.get("/by-failure-mode/{failure_mode_id}", response_model=list[schemas.FailureEffect])
def read_effects_by_failure_mode(
    failure_mode_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.get_effects_by_failure_mode(db, failure_mode_id=failure_mode_id)