from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud

router = APIRouter(prefix="/fmeas", tags=["fmeas"])


@router.post("/", response_model=schemas.FMEA)
def create_fmea(
    fmea: schemas.FMEACreate,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.create_fmea(db=db, fmea=fmea)


@router.get("/", response_model=list[schemas.FMEA])
def read_fmeas(
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    return crud.get_fmeas(db, skip=skip, limit=limit)


@router.get("/{fmea_id}", response_model=schemas.FMEA)
def read_fmea(
    fmea_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    db_fmea = crud.get_fmea(db, fmea_id=fmea_id)
    if db_fmea is None:
        raise HTTPException(status_code=404, detail="FMEA not found")
    return db_fmea


@router.put("/{fmea_id}", response_model=schemas.FMEA)
def update_fmea(
    fmea_id: int,
    fmea_update: schemas.FMEAUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    db_fmea = crud.update_fmea(db, fmea_id=fmea_id, fmea_update=fmea_update)
    if db_fmea is None:
        raise HTTPException(status_code=404, detail="FMEA not found")
    return db_fmea


@router.delete("/{fmea_id}")
def delete_fmea(
    fmea_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    success = crud.delete_fmea(db, fmea_id=fmea_id)
    if not success:
        raise HTTPException(status_code=404, detail="FMEA not found")
    return {"message": "FMEA deleted successfully"}


@router.get("/by-asset/{asset_id}", response_model=list[schemas.FMEA])
def read_fmeas_by_asset(
    asset_id: str,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.get_fmeas_by_asset_id(db, asset_id=asset_id)