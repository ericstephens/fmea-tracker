from sqlalchemy.orm import Session
from datetime import datetime

from ..db import models
from . import schemas


# Project CRUD operations
def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()


def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        name=project.name,
        description=project.description
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, project_id: int, project: schemas.ProjectUpdate):
    db_project = get_project(db, project_id)
    if db_project:
        update_data = project.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        db_project.updated_at = datetime.now()
        db.commit()
        db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project


# FMEA CRUD operations
def get_fmea(db: Session, fmea_id: int):
    return db.query(models.FMEA).filter(models.FMEA.id == fmea_id).first()


def get_fmeas_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.FMEA).filter(models.FMEA.project_id == project_id).offset(skip).limit(limit).all()


def create_fmea(db: Session, fmea: schemas.FMEACreate, project_id: int):
    db_fmea = models.FMEA(
        project_id=project_id,
        item=fmea.item,
        function=fmea.function
    )
    db.add(db_fmea)
    db.commit()
    db.refresh(db_fmea)
    return db_fmea


def update_fmea(db: Session, fmea_id: int, fmea: schemas.FMEAUpdate):
    db_fmea = get_fmea(db, fmea_id)
    if db_fmea:
        update_data = fmea.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_fmea, key, value)
        db_fmea.updated_at = datetime.now()
        db.commit()
        db.refresh(db_fmea)
    return db_fmea


def delete_fmea(db: Session, fmea_id: int):
    db_fmea = get_fmea(db, fmea_id)
    if db_fmea:
        db.delete(db_fmea)
        db.commit()
    return db_fmea


# Failure Mode CRUD operations
def get_failure_mode(db: Session, failure_mode_id: int):
    return db.query(models.FailureMode).filter(models.FailureMode.id == failure_mode_id).first()


def get_failure_modes_by_fmea(db: Session, fmea_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.FailureMode).filter(models.FailureMode.fmea_id == fmea_id).offset(skip).limit(limit).all()


def create_failure_mode(db: Session, failure_mode: schemas.FailureModeCreate, fmea_id: int):
    db_failure_mode = models.FailureMode(
        fmea_id=fmea_id,
        description=failure_mode.description,
        potential_causes=failure_mode.potential_causes,
        potential_effects=failure_mode.potential_effects,
        severity=failure_mode.severity,
        occurrence=failure_mode.occurrence,
        detection=failure_mode.detection,
        rpn=failure_mode.rpn,
        status=failure_mode.status
    )
    db.add(db_failure_mode)
    db.commit()
    db.refresh(db_failure_mode)
    return db_failure_mode


def update_failure_mode(db: Session, failure_mode_id: int, failure_mode: schemas.FailureModeUpdate):
    db_failure_mode = get_failure_mode(db, failure_mode_id)
    if db_failure_mode:
        update_data = failure_mode.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_failure_mode, key, value)
        db_failure_mode.updated_at = datetime.now()
        db.commit()
        db.refresh(db_failure_mode)
    return db_failure_mode


def delete_failure_mode(db: Session, failure_mode_id: int):
    db_failure_mode = get_failure_mode(db, failure_mode_id)
    if db_failure_mode:
        db.delete(db_failure_mode)
        db.commit()
    return db_failure_mode


# Action CRUD operations
def get_action(db: Session, action_id: int):
    return db.query(models.Action).filter(models.Action.id == action_id).first()


def get_actions_by_failure_mode(db: Session, failure_mode_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Action).filter(models.Action.failure_mode_id == failure_mode_id).offset(skip).limit(limit).all()


def create_action(db: Session, action: schemas.ActionCreate, failure_mode_id: int):
    db_action = models.Action(
        failure_mode_id=failure_mode_id,
        description=action.description,
        owner=action.owner,
        due_date=action.due_date,
        completed=action.completed,
        completion_date=action.completion_date
    )
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action


def update_action(db: Session, action_id: int, action: schemas.ActionUpdate):
    db_action = get_action(db, action_id)
    if db_action:
        update_data = action.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_action, key, value)
        db_action.updated_at = datetime.now()
        db.commit()
        db.refresh(db_action)
    return db_action


def delete_action(db: Session, action_id: int):
    db_action = get_action(db, action_id)
    if db_action:
        db.delete(db_action)
        db.commit()
    return db_action
