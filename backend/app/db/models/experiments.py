from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_image_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_image_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_image_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_features: Mapped[dict[str, object] | None] = mapped_column(
        JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    runs: Mapped[list["ExperimentRun"]] = relationship(
        back_populates="experiment",
        cascade="all, delete-orphan",
        order_by="ExperimentRun.created_at",
    )


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    experiment_id: Mapped[str] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    processing_id: Mapped[str] = mapped_column(String(36), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(64), nullable=False)
    parameters: Mapped[dict[str, str | int | float | bool]] = mapped_column(
        JSON, nullable=False
    )
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    output_url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    experiment: Mapped[Experiment] = relationship(back_populates="runs")
