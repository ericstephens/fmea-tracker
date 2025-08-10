from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from db.models import FMEA, FailureMode, Action, FailureCause, FailureEffect, Control
from . import schemas


def get_fmea(db: Session, fmea_id: int) -> Optional[FMEA]:
    return db.scalar(select(FMEA).where(FMEA.id == fmea_id))


def get_fmeas(db: Session, skip: int = 0, limit: int = 100) -> list[FMEA]:
    return list(db.scalars(select(FMEA).offset(skip).limit(limit)).all())


def get_fmeas_by_asset_id(db: Session, asset_id: str) -> list[FMEA]:
    return list(db.scalars(select(FMEA).where(FMEA.asset_id == asset_id)).all())


def create_fmea(db: Session, fmea: schemas.FMEACreate) -> FMEA:
    db_fmea = FMEA(**fmea.model_dump())
    db.add(db_fmea)
    db.commit()
    db.refresh(db_fmea)
    return db_fmea


def update_fmea(db: Session, fmea_id: int, fmea_update: schemas.FMEAUpdate) -> Optional[FMEA]:
    db_fmea = get_fmea(db, fmea_id)
    if db_fmea:
        update_data = fmea_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_fmea, field, value)
        db.commit()
        db.refresh(db_fmea)
    return db_fmea


def delete_fmea(db: Session, fmea_id: int) -> bool:
    db_fmea = get_fmea(db, fmea_id)
    if db_fmea:
        db.delete(db_fmea)
        db.commit()
        return True
    return False


def get_failure_mode(db: Session, failure_mode_id: int) -> Optional[FailureMode]:
    return db.scalar(select(FailureMode).where(FailureMode.id == failure_mode_id))


def get_failure_modes_by_fmea(db: Session, fmea_id: int) -> list[FailureMode]:
    return list(db.scalars(select(FailureMode).where(FailureMode.fmea_id == fmea_id)).all())


def create_failure_mode(db: Session, failure_mode: schemas.FailureModeCreate) -> FailureMode:
    db_failure_mode = FailureMode(**failure_mode.model_dump())
    db.add(db_failure_mode)
    db.commit()
    db.refresh(db_failure_mode)
    return db_failure_mode


def update_failure_mode(db: Session, failure_mode_id: int, failure_mode_update: schemas.FailureModeUpdate) -> Optional[FailureMode]:
    db_failure_mode = get_failure_mode(db, failure_mode_id)
    if db_failure_mode:
        update_data = failure_mode_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_failure_mode, field, value)
        db.commit()
        db.refresh(db_failure_mode)
    return db_failure_mode


def delete_failure_mode(db: Session, failure_mode_id: int) -> bool:
    db_failure_mode = get_failure_mode(db, failure_mode_id)
    if db_failure_mode:
        db.delete(db_failure_mode)
        db.commit()
        return True
    return False


def get_actions_by_failure_mode(db: Session, failure_mode_id: int) -> list[Action]:
    return list(db.scalars(select(Action).where(Action.failure_mode_id == failure_mode_id)).all())


def create_action(db: Session, action: schemas.ActionCreate) -> Action:
    db_action = Action(**action.model_dump())
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action


def update_action(db: Session, action_id: int, action_update: schemas.ActionUpdate) -> Optional[Action]:
    db_action = db.scalar(select(Action).where(Action.id == action_id))
    if db_action:
        update_data = action_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_action, field, value)
        db.commit()
        db.refresh(db_action)
    return db_action


def delete_action(db: Session, action_id: int) -> bool:
    db_action = db.scalar(select(Action).where(Action.id == action_id))
    if db_action:
        db.delete(db_action)
        db.commit()
        return True
    return False


def get_causes_by_failure_mode(db: Session, failure_mode_id: int) -> list[FailureCause]:
    return list(db.scalars(select(FailureCause).where(FailureCause.failure_mode_id == failure_mode_id)).all())


def create_failure_cause(db: Session, cause: schemas.FailureCauseCreate) -> FailureCause:
    db_cause = FailureCause(**cause.model_dump())
    db.add(db_cause)
    db.commit()
    db.refresh(db_cause)
    return db_cause


def update_failure_cause(db: Session, cause_id: int, cause_update: schemas.FailureCauseUpdate) -> Optional[FailureCause]:
    db_cause = db.scalar(select(FailureCause).where(FailureCause.id == cause_id))
    if db_cause:
        update_data = cause_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cause, field, value)
        db.commit()
        db.refresh(db_cause)
    return db_cause


def delete_failure_cause(db: Session, cause_id: int) -> bool:
    db_cause = db.scalar(select(FailureCause).where(FailureCause.id == cause_id))
    if db_cause:
        db.delete(db_cause)
        db.commit()
        return True
    return False


def get_effects_by_failure_mode(db: Session, failure_mode_id: int) -> list[FailureEffect]:
    return list(db.scalars(select(FailureEffect).where(FailureEffect.failure_mode_id == failure_mode_id)).all())


def create_failure_effect(db: Session, effect: schemas.FailureEffectCreate) -> FailureEffect:
    db_effect = FailureEffect(**effect.model_dump())
    db.add(db_effect)
    db.commit()
    db.refresh(db_effect)
    return db_effect


def update_failure_effect(db: Session, effect_id: int, effect_update: schemas.FailureEffectUpdate) -> Optional[FailureEffect]:
    db_effect = db.scalar(select(FailureEffect).where(FailureEffect.id == effect_id))
    if db_effect:
        update_data = effect_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_effect, field, value)
        db.commit()
        db.refresh(db_effect)
    return db_effect


def delete_failure_effect(db: Session, effect_id: int) -> bool:
    db_effect = db.scalar(select(FailureEffect).where(FailureEffect.id == effect_id))
    if db_effect:
        db.delete(db_effect)
        db.commit()
        return True
    return False


def get_controls_by_failure_mode(db: Session, failure_mode_id: int) -> list[Control]:
    return list(db.scalars(select(Control).where(Control.failure_mode_id == failure_mode_id)).all())


def create_control(db: Session, control: schemas.ControlCreate) -> Control:
    db_control = Control(**control.model_dump())
    db.add(db_control)
    db.commit()
    db.refresh(db_control)
    return db_control


def update_control(db: Session, control_id: int, control_update: schemas.ControlUpdate) -> Optional[Control]:
    db_control = db.scalar(select(Control).where(Control.id == control_id))
    if db_control:
        update_data = control_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_control, field, value)
        db.commit()
        db.refresh(db_control)
    return db_control


def delete_control(db: Session, control_id: int) -> bool:
    db_control = db.scalar(select(Control).where(Control.id == control_id))
    if db_control:
        db.delete(db_control)
        db.commit()
        return True
    return False