import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.water_nutrition import MealType


class WaterGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    daily_goal_ml: int
    updated_at: datetime


class WaterGoalUpdate(BaseModel):
    daily_goal_ml: int


class WaterIntakeCreate(BaseModel):
    amount_ml: int


class WaterIntakeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    amount_ml: int
    date: datetime


class WaterReminderSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    is_enabled: bool
    interval_minutes: int
    start_hour: int
    start_minute: int
    end_hour: int
    end_minute: int


class WaterReminderSettingsUpdate(BaseModel):
    is_enabled: bool
    interval_minutes: int
    start_hour: int
    start_minute: int
    end_hour: int
    end_minute: int


class FoodItemCreate(BaseModel):
    name: str
    grams: float = 0
    calories: float = 0
    proteins: float = 0
    fats: float = 0
    carbs: float = 0
    meal_type: MealType
    date: datetime | None = None


class FoodItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    grams: float
    calories: float
    proteins: float
    fats: float
    carbs: float
    meal_type: MealType
    date: datetime


class NutritionGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    daily_calorie_goal: float
    protein_goal_grams: float
    fat_goal_grams: float
    carb_goal_grams: float
    updated_at: datetime


class NutritionGoalUpdate(BaseModel):
    daily_calorie_goal: float
    protein_goal_grams: float
    fat_goal_grams: float
    carb_goal_grams: float
