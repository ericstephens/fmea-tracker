from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Computed,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class FMEA(Base):
    __tablename__ = "fmeas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Correlate an external asset identifier to the FMEA record
    asset_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # Optional human-friendly title/identifier for this FMEA
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Simple integer versioning per asset
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("asset_id", "version", name="uq_fmea_asset_version"),
    )


class FailureMode(Base):
    __tablename__ = "failure_modes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Link each failure mode to a specific FMEA record (asset + version)
    fmea_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fmeas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    occurrence: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    detection: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    # rpn as a generated stored column in Postgres
    rpn: Mapped[int] = mapped_column(
        Integer,
        Computed("(severity * occurrence * detection)", persisted=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("fmea_id", "name", name="uq_failure_mode_fmea_name"),
        CheckConstraint("severity BETWEEN 1 AND 10", name="ck_failure_modes_severity_range"),
        CheckConstraint("occurrence BETWEEN 1 AND 10", name="ck_failure_modes_occurrence_range"),
        CheckConstraint("detection BETWEEN 1 AND 10", name="ck_failure_modes_detection_range"),
    )

    # Relationship to actions (for convenience; not strictly required for tests)
    actions: Mapped[list["Action"]] = relationship(
        back_populates="failure_mode",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    causes: Mapped[list["FailureCause"]] = relationship(
        back_populates="failure_mode",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    effects: Mapped[list["FailureEffect"]] = relationship(
        back_populates="failure_mode",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    controls: Mapped[list["Control"]] = relationship(
        back_populates="failure_mode",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<FailureMode id={self.id} fmea_id={self.fmea_id} "
            f"name={self.name!r} severity={self.severity} "
            f"occurrence={self.occurrence} detection={self.detection} rpn={self.rpn}>"
        )


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    failure_mode_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("failure_modes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="open"
    )  # open, in_progress, closed, deferred
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    failure_mode: Mapped[FailureMode] = relationship(back_populates="actions")

    __table_args__ = (
        CheckConstraint(
            "status IN ('open','in_progress','closed','deferred')",
            name="ck_actions_status_valid",
        ),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Action id={self.id} failure_mode_id={self.failure_mode_id} "
            f"status={self.status!r} owner={self.owner!r} due_date={self.due_date}>"
        )


class FailureCause(Base):
    __tablename__ = "failure_causes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    failure_mode_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("failure_modes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    failure_mode: Mapped[FailureMode] = relationship(back_populates="causes")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FailureCause id={self.id} fm_id={self.failure_mode_id}>"


class FailureEffect(Base):
    __tablename__ = "failure_effects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    failure_mode_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("failure_modes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    failure_mode: Mapped[FailureMode] = relationship(back_populates="effects")

    __table_args__ = (
        CheckConstraint(
            "level IS NULL OR level IN ('local','next_higher','end_user')",
            name="ck_failure_effects_level_valid",
        ),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FailureEffect id={self.id} fm_id={self.failure_mode_id} level={self.level}>"


class Control(Base):
    __tablename__ = "controls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    failure_mode_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("failure_modes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # prevention/detection
    description: Mapped[str] = mapped_column(Text, nullable=False)
    method_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    failure_mode: Mapped[FailureMode] = relationship(back_populates="controls")

    __table_args__ = (
        CheckConstraint(
            "type IN ('prevention','detection')",
            name="ck_controls_type_valid",
        ),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Control id={self.id} fm_id={self.failure_mode_id} type={self.type}>"
