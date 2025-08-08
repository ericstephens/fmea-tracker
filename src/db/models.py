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
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<FailureMode id={self.id} fmea_id={self.fmea_id} "
            f"name={self.name!r} severity={self.severity} "
            f"occurrence={self.occurrence} detection={self.detection} rpn={self.rpn}>"
        )
