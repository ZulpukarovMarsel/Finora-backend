from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.water_nutrition import WaterGoal, WaterIntake, WaterReminderSettings
from app.schemas.water_nutrition import (
    WaterGoalRead,
    WaterGoalUpdate,
    WaterIntakeCreate,
    WaterIntakeRead,
    WaterReminderSettingsRead,
    WaterReminderSettingsUpdate,
)

router = APIRouter(prefix="/water", tags=["water"])


def _get_or_create_goal(db: Session, user: User) -> WaterGoal:
    goal = db.query(WaterGoal).filter(WaterGoal.user_id == user.id).first()
    if not goal:
        goal = WaterGoal(user_id=user.id)
        db.add(goal)
        db.commit()
        db.refresh(goal)
    return goal


@router.get("/goal", response_model=WaterGoalRead)
def get_goal(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_or_create_goal(db, user)


@router.put("/goal", response_model=WaterGoalRead)
def set_goal(payload: WaterGoalUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = _get_or_create_goal(db, user)
    goal.daily_goal_ml = payload.daily_goal_ml
    goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/intakes", response_model=list[WaterIntakeRead])
def list_intakes(on_date: date | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    target = on_date or date.today()
    start = datetime.combine(target, datetime.min.time())
    end = start + timedelta(days=1)
    return (
        db.query(WaterIntake)
        .filter(WaterIntake.user_id == user.id, WaterIntake.date >= start, WaterIntake.date < end)
        .order_by(WaterIntake.date.desc())
        .all()
    )


@router.post("/intakes", response_model=WaterIntakeRead, status_code=201)
def add_intake(payload: WaterIntakeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    intake = WaterIntake(user_id=user.id, amount_ml=payload.amount_ml)
    db.add(intake)
    db.commit()
    db.refresh(intake)
    return intake


@router.get("/reminder-settings", response_model=WaterReminderSettingsRead)
def get_reminder_settings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    settings = db.query(WaterReminderSettings).filter(WaterReminderSettings.user_id == user.id).first()
    if not settings:
        settings = WaterReminderSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("/reminder-settings", response_model=WaterReminderSettingsRead)
def update_reminder_settings(
    payload: WaterReminderSettingsUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    settings = db.query(WaterReminderSettings).filter(WaterReminderSettings.user_id == user.id).first()
    if not settings:
        settings = WaterReminderSettings(user_id=user.id)
        db.add(settings)
    for field, value in payload.model_dump().items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings
