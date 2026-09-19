import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDPKMixin


class LearningGoalKind(str, enum.Enum):
    language = "language"
    math = "math"
    course = "course"
    custom = "custom"


class MathOperation(str, enum.Enum):
    addition = "addition"
    subtraction = "subtraction"
    multiplication = "multiplication"
    division = "division"
    percentage = "percentage"
    power = "power"


class MathDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class LearningGoal(UUIDPKMixin, Base):
    __tablename__ = "learning_goals"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    icon_name: Mapped[str] = mapped_column(String(80), default="graduationcap.fill")
    kind: Mapped[LearningGoalKind] = mapped_column(Enum(LearningGoalKind, name="learning_goal_kind"), default=LearningGoalKind.custom)
    target_description: Mapped[str] = mapped_column(String(300), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)

    sessions: Mapped[list["LearningSession"]] = relationship(back_populates="goal", cascade="all, delete-orphan")


class LearningSession(UUIDPKMixin, Base):
    __tablename__ = "learning_sessions"

    goal_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("learning_goals.id"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    progress_note: Mapped[str] = mapped_column(String(300), default="")

    goal: Mapped["LearningGoal"] = relationship(back_populates="sessions")


class Word(UUIDPKMixin, Base):
    __tablename__ = "words"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    term: Mapped[str] = mapped_column(String(200))
    translation: Mapped[str] = mapped_column(String(200))
    language_code: Mapped[str] = mapped_column(String(8), default="de")
    is_learned: Mapped[bool] = mapped_column(Boolean, default=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class MathExerciseRecord(UUIDPKMixin, Base):
    __tablename__ = "math_exercise_records"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    question_text: Mapped[str] = mapped_column(String(200))
    correct_answer: Mapped[float] = mapped_column(Float)
    user_answer: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    operation: Mapped[MathOperation] = mapped_column(Enum(MathOperation, name="math_operation"))
    difficulty: Mapped[MathDifficulty] = mapped_column(Enum(MathDifficulty, name="math_difficulty"), default=MathDifficulty.medium)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
