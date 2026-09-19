import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.learning import LearningGoalKind, MathDifficulty, MathOperation


class LearningGoalCreate(BaseModel):
    title: str
    icon_name: str = "graduationcap.fill"
    kind: LearningGoalKind = LearningGoalKind.custom
    target_description: str = ""


class LearningGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    icon_name: str
    kind: LearningGoalKind
    target_description: str
    created_at: datetime
    current_streak: int


class LearningSessionCreate(BaseModel):
    duration_minutes: int = 0
    progress_note: str = ""


class LearningSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    goal_id: uuid.UUID
    date: datetime
    duration_minutes: int
    progress_note: str


class WordCreate(BaseModel):
    term: str
    translation: str
    language_code: str = "de"


class WordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    term: str
    translation: str
    language_code: str
    is_learned: bool
    last_reviewed_at: datetime | None
    created_at: datetime


class WordReview(BaseModel):
    is_learned: bool


class MathExerciseCreate(BaseModel):
    question_text: str
    correct_answer: float
    user_answer: float | None = None
    is_correct: bool
    operation: MathOperation
    difficulty: MathDifficulty = MathDifficulty.medium


class MathExerciseRead(MathExerciseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    date: datetime
