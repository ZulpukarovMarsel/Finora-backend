import enum
import uuid
from datetime import date, datetime

from sqlalchemy import ARRAY, Boolean, Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDPKMixin


class TaskRepeatRule(str, enum.Enum):
    once = "once"
    daily = "daily"
    weekdays = "weekdays"
    weekly = "weekly"
    monthly = "monthly"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class WakeConfirmationMode(str, enum.Enum):
    none = "none"
    tap = "tap"
    photo = "photo"
    mathProblem = "mathProblem"
    vocabGeneral = "vocabGeneral"
    vocabLanguage = "vocabLanguage"


class AlarmSound(str, enum.Enum):
    classic = "classic"
    gentle = "gentle"
    urgent = "urgent"
    custom = "custom"


class TaskItem(UUIDPKMixin, Base):
    __tablename__ = "tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    icon_name: Mapped[str] = mapped_column(String(80), default="checkmark.circle")
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(String(2000), default="")
    repeat_rule: Mapped[TaskRepeatRule] = mapped_column(Enum(TaskRepeatRule, name="task_repeat_rule"), default=TaskRepeatRule.once)
    weekdays: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority, name="task_priority"), default=TaskPriority.medium)
    category_name: Mapped[str] = mapped_column(String(80), default="Общее")
    reminder_offset_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, default=5)

    is_alarm: Mapped[bool] = mapped_column(Boolean, default=False)
    wake_confirmation_mode: Mapped[WakeConfirmationMode] = mapped_column(
        Enum(WakeConfirmationMode, name="wake_confirmation_mode"), default=WakeConfirmationMode.none
    )
    wake_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Which StudyLanguage to draw words from when
    # wake_confirmation_mode == vocabLanguage.
    alarm_language_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("study_languages.id"), nullable=True)
    alarm_sound: Mapped[AlarmSound] = mapped_column(Enum(AlarmSound, name="alarm_sound"), default=AlarmSound.classic)
    # Set only when alarm_sound == custom — a song picked from the user's
    # Music library on their device (playable only client-side; the
    # backend just stores which one was chosen so it stays in sync across
    # the user's devices).
    custom_song_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    custom_song_persistent_id: Mapped[int | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Habit(UUIDPKMixin, Base):
    __tablename__ = "habits"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    icon_name: Mapped[str] = mapped_column(String(80), default="flame.fill")
    color_hex: Mapped[str] = mapped_column(String(8), default="FF5FA2")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    freezes_available: Mapped[int] = mapped_column(Integer, default=1)

    completions: Mapped[list["HabitCompletion"]] = relationship(
        back_populates="habit", cascade="all, delete-orphan"
    )


class HabitCompletion(UUIDPKMixin, Base):
    __tablename__ = "habit_completions"

    habit_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("habits.id"))
    date: Mapped[date] = mapped_column(Date, index=True)
    used_freeze: Mapped[bool] = mapped_column(Boolean, default=False)

    habit: Mapped["Habit"] = relationship(back_populates="completions")
