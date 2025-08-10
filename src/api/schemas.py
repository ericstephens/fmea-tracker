from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FMEABase(BaseModel):
    asset_id: str
    title: str
    description: Optional[str] = None
    version: int = 1
    is_active: bool = True
    status: str = "draft"
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    supersedes_fmea_id: Optional[int] = None


class FMEACreate(FMEABase):
    pass


class FMEAUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    updated_by: Optional[str] = None
    supersedes_fmea_id: Optional[int] = None


class FMEA(FMEABase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class FailureModeBase(BaseModel):
    fmea_id: int
    name: str
    severity: int = 1
    occurrence: int = 1
    detection: int = 10


class FailureModeCreate(FailureModeBase):
    pass


class FailureModeUpdate(BaseModel):
    name: Optional[str] = None
    severity: Optional[int] = None
    occurrence: Optional[int] = None
    detection: Optional[int] = None


class FailureMode(FailureModeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    rpn: int
    created_at: datetime


class ActionBase(BaseModel):
    failure_mode_id: int
    description: str
    owner: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "open"
    notes: Optional[str] = None


class ActionCreate(ActionBase):
    pass


class ActionUpdate(BaseModel):
    description: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    closed_at: Optional[datetime] = None


class Action(ActionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    closed_at: Optional[datetime] = None


class FailureCauseBase(BaseModel):
    failure_mode_id: int
    description: str


class FailureCauseCreate(FailureCauseBase):
    pass


class FailureCauseUpdate(BaseModel):
    description: Optional[str] = None


class FailureCause(FailureCauseBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


class FailureEffectBase(BaseModel):
    failure_mode_id: int
    description: str
    level: Optional[str] = None


class FailureEffectCreate(FailureEffectBase):
    pass


class FailureEffectUpdate(BaseModel):
    description: Optional[str] = None
    level: Optional[str] = None


class FailureEffect(FailureEffectBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


class ControlBase(BaseModel):
    failure_mode_id: int
    type: str
    description: str
    method_ref: Optional[str] = None


class ControlCreate(ControlBase):
    pass


class ControlUpdate(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None
    method_ref: Optional[str] = None


class Control(ControlBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime