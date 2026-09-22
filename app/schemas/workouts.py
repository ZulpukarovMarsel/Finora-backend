import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class WorkoutSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    default_rest_seconds: int
    target_total_minutes: int


class WorkoutSettingsUpdate(BaseModel):
    default_rest_seconds: int
    target_total_minutes: int


class WorkoutExerciseCreate(BaseModel):
    name: str
    reps: int
    sets: int
    rest_seconds: int | None = None
    order_index: int = 0
    weight_kg: float | None = None
    video_url: str | None = None


class WorkoutExerciseRead(WorkoutExerciseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    plan_id: uuid.UUID


class WorkoutPlanCreate(BaseModel):
    name: str
    weekdays: list[int]
    scheduled_hour: int = 18
    scheduled_minute: int = 0
    exercises: list[WorkoutExerciseCreate] = []


class WorkoutPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    weekdays: list[int]
    scheduled_hour: int
    scheduled_minute: int
    created_at: datetime
    exercises: list[WorkoutExerciseRead] = []


class WorkoutCompletionCreate(BaseModel):
    duration_seconds: int = 0


class WorkoutCompletionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    plan_id: uuid.UUID
    date: date
    duration_seconds: int
