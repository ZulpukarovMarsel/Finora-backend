import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.tasks import AlarmSound, TaskPriority, TaskRepeatRule, WakeConfirmationMode


class TaskCreate(BaseModel):
    title: str
    icon_name: str = "checkmark.circle"
    scheduled_date: datetime
    notes: str = ""
    repeat_rule: TaskRepeatRule = TaskRepeatRule.once
    weekdays: list[int] = []
    priority: TaskPriority = TaskPriority.medium
    category_name: str = "Общее"
    reminder_offset_minutes: int | None = 5
    is_alarm: bool = False
    wake_confirmation_mode: WakeConfirmationMode = WakeConfirmationMode.none
    alarm_language_id: uuid.UUID | None = None
    alarm_sound: AlarmSound = AlarmSound.classic
    custom_song_title: str | None = None
    custom_song_persistent_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    scheduled_date: datetime | None = None
    is_done: bool | None = None
    notes: str | None = None
    priority: TaskPriority | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    icon_name: str
    scheduled_date: datetime
    is_done: bool
    notes: str
    repeat_rule: TaskRepeatRule
    weekdays: list[int]
    priority: TaskPriority
    category_name: str
    reminder_offset_minutes: int | None
    is_alarm: bool
    wake_confirmation_mode: WakeConfirmationMode
    wake_confirmed_at: datetime | None
    alarm_language_id: uuid.UUID | None
    alarm_sound: AlarmSound
    custom_song_title: str | None
    custom_song_persistent_id: int | None
    created_at: datetime


class HabitCreate(BaseModel):
    name: str
    icon_name: str = "flame.fill"
    color_hex: str = "FF5FA2"


class HabitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    icon_name: str
    color_hex: str
    created_at: datetime
    current_streak: int
    longest_streak: int
    freezes_available: int


class HabitCompletionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    date: date
    used_freeze: bool
