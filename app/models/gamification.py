import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDPKMixin


class XPSource(str, enum.Enum):
    wakeOnTime = "wakeOnTime"
    workout = "workout"
    reading = "reading"
    readingPages = "readingPages"
    germanWords = "germanWords"
    math = "math"
    bookFinished = "bookFinished"
    task = "task"
    habit = "habit"
    water = "water"
    other = "other"


class XPRecord(UUIDPKMixin, Base):
    __tablename__ = "xp_records"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    amount: Mapped[int] = mapped_column(Integer)
    source: Mapped[XPSource] = mapped_column(Enum(XPSource, name="xp_source"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    note: Mapped[str] = mapped_column(String(300), default="")


class Achievement(UUIDPKMixin, Base):
    __tablename__ = "achievements"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    icon_name: Mapped[str] = mapped_column(String(80), default="star.fill")
    achieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    progress_current: Mapped[int] = mapped_column(Integer, default=0)
    progress_target: Mapped[int] = mapped_column(Integer, default=1)


class DailySummary(UUIDPKMixin, Base):
    __tablename__ = "daily_summaries"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    tasks_total: Mapped[int] = mapped_column(Integer, default=0)
    water_ml: Mapped[int] = mapped_column(Integer, default=0)
    water_goal_ml: Mapped[int] = mapped_column(Integer, default=0)
    calories_consumed: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    calories_goal: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    workout_done: Mapped[bool] = mapped_column(Boolean, default=False)
    reading_minutes: Mapped[int] = mapped_column(Integer, default=0)
    income_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    expense_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    saved_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    mood_note: Mapped[str] = mapped_column(String(1000), default="")
