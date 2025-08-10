from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud

router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("/", response_model=schemas.Action)
def create_action(
    action: schemas.ActionCreate,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.create_action(db=db, action=action)


@router.put("/{action_id}", response_model=schemas.Action)
def update_action(
    action_id: int,
    action_update: schemas.ActionUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    db_action = crud.update_action(db, action_id=action_id, action_update=action_update)
    if db_action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return db_action


@router.delete("/{action_id}")
def delete_action(
    action_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    success = crud.delete_action(db, action_id=action_id)
    if not success:
        raise HTTPException(status_code=404, detail="Action not found")
    return {"message": "Action deleted successfully"}


@router.get("/by-failure-mode/{failure_mode_id}", response_model=list[schemas.Action])
def read_actions_by_failure_mode(
    failure_mode_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.get_actions_by_failure_mode(db, failure_mode_id=failure_mode_id)