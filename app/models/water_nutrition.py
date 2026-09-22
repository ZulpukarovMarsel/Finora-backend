import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDPKMixin


class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class WaterGoal(UUIDPKMixin, Base):
    __tablename__ = "water_goals"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    daily_goal_ml: Mapped[int] = mapped_column(Integer, default=3000)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class WaterIntake(UUIDPKMixin, Base):
    __tablename__ = "water_intakes"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    amount_ml: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class WaterReminderSettings(UUIDPKMixin, Base):
    __tablename__ = "water_reminder_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    start_hour: Mapped[int] = mapped_column(Integer, default=8)
    start_minute: Mapped[int] = mapped_column(Integer, default=0)
    end_hour: Mapped[int] = mapped_column(Integer, default=22)
    end_minute: Mapped[int] = mapped_column(Integer, default=0)


class FoodItem(UUIDPKMixin, Base):
    __tablename__ = "food_items"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    grams: Mapped[float] = mapped_column(Float, default=0)
    calories: Mapped[float] = mapped_column(Float, default=0)
    proteins: Mapped[float] = mapped_column(Float, default=0)
    fats: Mapped[float] = mapped_column(Float, default=0)
    carbs: Mapped[float] = mapped_column(Float, default=0)
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType, name="meal_type"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)


# Single source of truth for the daily nutrition goal — mirrors the iOS
# client's `NutritionGoal` SwiftData model. Previously the backend had no
# equivalent at all; Settings/Today/Profile screens on the client now all
# read/write this same record.
class NutritionGoal(UUIDPKMixin, Base):
    __tablename__ = "nutrition_goals"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    daily_calorie_goal: Mapped[float] = mapped_column(Float, default=2500)
    protein_goal_grams: Mapped[float] = mapped_column(Float, default=120)
    fat_goal_grams: Mapped[float] = mapped_column(Float, default=80)
    carb_goal_grams: Mapped[float] = mapped_column(Float, default=300)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
