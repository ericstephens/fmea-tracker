from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# FMEA schemas
class FMEABase(BaseModel):
    item: str
    function: str


class FMEACreate(FMEABase):
    pass


class FMEAUpdate(FMEABase):
    pass


class FMEA(FMEABase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Failure Mode schemas
class FailureModeBase(BaseModel):
    description: str
    potential_causes: Optional[str] = None
    potential_effects: str
    severity: int
    occurrence: int
    detection: int
    rpn: int
    status: str = "open"


class FailureModeCreate(FailureModeBase):
    pass


class FailureModeUpdate(FailureModeBase):
    pass


class FailureMode(FailureModeBase):
    id: int
    fmea_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Action schemas
class ActionBase(BaseModel):
    description: str
    owner: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: bool = False
    completion_date: Optional[datetime] = None


class ActionCreate(ActionBase):
    pass


class ActionUpdate(ActionBase):
    pass


class Action(ActionBase):
    id: int
    failure_mode_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Full schemas with relationships
class ActionWithDetails(Action):
    pass


class FailureModeWithActions(FailureMode):
    actions: List[ActionWithDetails] = []


class FMEAWithFailureModes(FMEA):
    failure_modes: List[FailureModeWithActions] = []


class ProjectWithFMEAs(Project):
    fmeas: List[FMEAWithFailureModes] = []
