import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.gamification import XPSource


class XPAward(BaseModel):
    amount: int
    source: XPSource
    note: str = ""


class XPRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    amount: int
    source: XPSource
    date: datetime
    note: str


class DailySummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    date: date
    tasks_completed: int
    tasks_total: int
    water_ml: int
    water_goal_ml: int
    calories_consumed: Decimal
    calories_goal: Decimal
    workout_done: bool
    reading_minutes: int
    income_total: Decimal
    expense_total: Decimal
    saved_total: Decimal
    xp_earned: int
    mood_note: str


class DailySummaryUpdate(BaseModel):
    mood_note: str | None = None
    workout_done: bool | None = None
