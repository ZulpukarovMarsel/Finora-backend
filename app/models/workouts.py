import uuid
from datetime import date, datetime

from sqlalchemy import ARRAY, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDPKMixin


class WorkoutPlan(UUIDPKMixin, Base):
    __tablename__ = "workout_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    # ISO weekdays this plan runs on: 1 = Monday ... 7 = Sunday.
    weekdays: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    scheduled_hour: Mapped[int] = mapped_column(Integer, default=18)
    scheduled_minute: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", order_by="WorkoutExercise.order_index"
    )


class WorkoutExercise(UUIDPKMixin, Base):
    __tablename__ = "workout_exercises"

    plan_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("workout_plans.id"))
    name: Mapped[str] = mapped_column(String(120))
    reps: Mapped[int] = mapped_column(Integer)
    sets: Mapped[int] = mapped_column(Integer)
    # nil = use the user's global default rest time (WorkoutSettings).
    rest_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    # YouTube link or an uploaded-video URL — spec: "видео с техникой
    # выполнения (YouTube или загруженное)".
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    plan: Mapped["WorkoutPlan"] = relationship(back_populates="exercises")


class WorkoutSettings(UUIDPKMixin, Base):
    __tablename__ = "workout_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    default_rest_seconds: Mapped[int] = mapped_column(Integer, default=60)
    # Target total workout duration in minutes — default 90 (1.5h).
    target_total_minutes: Mapped[int] = mapped_column(Integer, default=90)


class WorkoutCompletion(UUIDPKMixin, Base):
    __tablename__ = "workout_completions"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("workout_plans.id"), index=True)
    date: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
