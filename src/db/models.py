from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class SeverityEnum(enum.Enum):
    MINOR = 1
    MODERATE = 2
    SIGNIFICANT = 3
    MAJOR = 4
    CATASTROPHIC = 5

class OccurrenceEnum(enum.Enum):
    REMOTE = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    VERY_HIGH = 5

class DetectionEnum(enum.Enum):
    VERY_HIGH = 1
    HIGH = 2
    MODERATE = 3
    LOW = 4
    REMOTE = 5

class StatusEnum(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    fmeas = relationship("FMEA", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"

class FMEA(Base):
    __tablename__ = "fmeas"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    item = Column(String(100), nullable=False)
    function = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="fmeas")
    failure_modes = relationship("FailureMode", back_populates="fmea", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FMEA(id={self.id}, item='{self.item}')>"

class FailureMode(Base):
    __tablename__ = "failure_modes"
    
    id = Column(Integer, primary_key=True, index=True)
    fmea_id = Column(Integer, ForeignKey("fmeas.id"), nullable=False)
    description = Column(Text, nullable=False)
    potential_causes = Column(Text)
    potential_effects = Column(Text, nullable=False)
    severity = Column(Integer, nullable=False)
    occurrence = Column(Integer, nullable=False)
    detection = Column(Integer, nullable=False)
    rpn = Column(Integer, nullable=False)  # Risk Priority Number
    status = Column(String(20), nullable=False, default=StatusEnum.OPEN.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    fmea = relationship("FMEA", back_populates="failure_modes")
    actions = relationship("Action", back_populates="failure_mode", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FailureMode(id={self.id}, description='{self.description[:20]}...', rpn={self.rpn})>"

class Action(Base):
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True, index=True)
    failure_mode_id = Column(Integer, ForeignKey("failure_modes.id"), nullable=False)
    description = Column(Text, nullable=False)
    owner = Column(String(100))
    due_date = Column(DateTime(timezone=True))
    completed = Column(Boolean, default=False)
    completion_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    failure_mode = relationship("FailureMode", back_populates="actions")
    
    def __repr__(self):
        return f"<Action(id={self.id}, description='{self.description[:20]}...', completed={self.completed})>"
