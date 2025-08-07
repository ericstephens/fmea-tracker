from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from ..db.database import get_db
from . import models, schemas, crud

app = FastAPI(title="FMEA Tracker API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FMEA Tracker API"}

# Projects endpoints
@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db=db, project=project)

@app.get("/projects/", response_model=list[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.update_project(db=db, project_id=project_id, project=project)

@app.delete("/projects/{project_id}", response_model=schemas.Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.delete_project(db=db, project_id=project_id)

# FMEA endpoints
@app.post("/projects/{project_id}/fmeas/", response_model=schemas.FMEA)
def create_fmea(project_id: int, fmea: schemas.FMEACreate, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.create_fmea(db=db, fmea=fmea, project_id=project_id)

@app.get("/projects/{project_id}/fmeas/", response_model=list[schemas.FMEA])
def read_fmeas(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    fmeas = crud.get_fmeas_by_project(db, project_id=project_id, skip=skip, limit=limit)
    return fmeas

@app.get("/fmeas/{fmea_id}", response_model=schemas.FMEA)
def read_fmea(fmea_id: int, db: Session = Depends(get_db)):
    db_fmea = crud.get_fmea(db, fmea_id=fmea_id)
    if db_fmea is None:
        raise HTTPException(status_code=404, detail="FMEA not found")
    return db_fmea

@app.put("/fmeas/{fmea_id}", response_model=schemas.FMEA)
def update_fmea(fmea_id: int, fmea: schemas.FMEAUpdate, db: Session = Depends(get_db)):
    db_fmea = crud.get_fmea(db, fmea_id=fmea_id)
    if db_fmea is None:
        raise HTTPException(status_code=404, detail="FMEA not found")
    return crud.update_fmea(db=db, fmea_id=fmea_id, fmea=fmea)

@app.delete("/fmeas/{fmea_id}", response_model=schemas.FMEA)
def delete_fmea(fmea_id: int, db: Session = Depends(get_db)):
    db_fmea = crud.get_fmea(db, fmea_id=fmea_id)
    if db_fmea is None:
        raise HTTPException(status_code=404, detail="FMEA not found")
    return crud.delete_fmea(db=db, fmea_id=fmea_id)

# Failure Mode endpoints
@app.post("/fmeas/{fmea_id}/failure-modes/", response_model=schemas.FailureMode)
def create_failure_mode(fmea_id: int, failure_mode: schemas.FailureModeCreate, db: Session = Depends(get_db)):
    db_fmea = crud.get_fmea(db, fmea_id=fmea_id)
    if db_fmea is None:
        raise HTTPException(status_code=404, detail="FMEA not found")
    return crud.create_failure_mode(db=db, failure_mode=failure_mode, fmea_id=fmea_id)

@app.get("/fmeas/{fmea_id}/failure-modes/", response_model=list[schemas.FailureMode])
def read_failure_modes(fmea_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_fmea = crud.get_fmea(db, fmea_id=fmea_id)
    if db_fmea is None:
        raise HTTPException(status_code=404, detail="FMEA not found")
    failure_modes = crud.get_failure_modes_by_fmea(db, fmea_id=fmea_id, skip=skip, limit=limit)
    return failure_modes

@app.get("/failure-modes/{failure_mode_id}", response_model=schemas.FailureMode)
def read_failure_mode(failure_mode_id: int, db: Session = Depends(get_db)):
    db_failure_mode = crud.get_failure_mode(db, failure_mode_id=failure_mode_id)
    if db_failure_mode is None:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    return db_failure_mode

@app.put("/failure-modes/{failure_mode_id}", response_model=schemas.FailureMode)
def update_failure_mode(failure_mode_id: int, failure_mode: schemas.FailureModeUpdate, db: Session = Depends(get_db)):
    db_failure_mode = crud.get_failure_mode(db, failure_mode_id=failure_mode_id)
    if db_failure_mode is None:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    return crud.update_failure_mode(db=db, failure_mode_id=failure_mode_id, failure_mode=failure_mode)

@app.delete("/failure-modes/{failure_mode_id}", response_model=schemas.FailureMode)
def delete_failure_mode(failure_mode_id: int, db: Session = Depends(get_db)):
    db_failure_mode = crud.get_failure_mode(db, failure_mode_id=failure_mode_id)
    if db_failure_mode is None:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    return crud.delete_failure_mode(db=db, failure_mode_id=failure_mode_id)

# Action endpoints
@app.post("/failure-modes/{failure_mode_id}/actions/", response_model=schemas.Action)
def create_action(failure_mode_id: int, action: schemas.ActionCreate, db: Session = Depends(get_db)):
    db_failure_mode = crud.get_failure_mode(db, failure_mode_id=failure_mode_id)
    if db_failure_mode is None:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    return crud.create_action(db=db, action=action, failure_mode_id=failure_mode_id)

@app.get("/failure-modes/{failure_mode_id}/actions/", response_model=list[schemas.Action])
def read_actions(failure_mode_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_failure_mode = crud.get_failure_mode(db, failure_mode_id=failure_mode_id)
    if db_failure_mode is None:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    actions = crud.get_actions_by_failure_mode(db, failure_mode_id=failure_mode_id, skip=skip, limit=limit)
    return actions

@app.get("/actions/{action_id}", response_model=schemas.Action)
def read_action(action_id: int, db: Session = Depends(get_db)):
    db_action = crud.get_action(db, action_id=action_id)
    if db_action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return db_action

@app.put("/actions/{action_id}", response_model=schemas.Action)
def update_action(action_id: int, action: schemas.ActionUpdate, db: Session = Depends(get_db)):
    db_action = crud.get_action(db, action_id=action_id)
    if db_action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return crud.update_action(db=db, action_id=action_id, action=action)

@app.delete("/actions/{action_id}", response_model=schemas.Action)
def delete_action(action_id: int, db: Session = Depends(get_db)):
    db_action = crud.get_action(db, action_id=action_id)
    if db_action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return crud.delete_action(db=db, action_id=action_id)
