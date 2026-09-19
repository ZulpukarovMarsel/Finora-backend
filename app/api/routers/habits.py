import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.tasks import Habit, HabitCompletion
from app.models.user import User
from app.schemas.tasks import HabitCreate, HabitRead

router = APIRouter(prefix="/habits", tags=["habits"])


@router.get("", response_model=list[HabitRead])
def list_habits(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Habit).filter(Habit.user_id == user.id).order_by(Habit.created_at).all()


@router.post("", response_model=HabitRead, status_code=201)
def create_habit(payload: HabitCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    habit = Habit(user_id=user.id, **payload.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.post("/{habit_id}/complete", response_model=HabitRead)
def complete_habit(habit_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Привычка не найдена")

    today = date.today()
    already_done = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit.id, HabitCompletion.date == today
    ).first()
    if already_done:
        return habit

    db.add(HabitCompletion(habit_id=habit.id, date=today))

    yesterday_done = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit.id, HabitCompletion.date == today - timedelta(days=1)
    ).first()
    if yesterday_done or habit.current_streak == 0:
        habit.current_streak += 1
    else:
        habit.current_streak = 1
    habit.longest_streak = max(habit.longest_streak, habit.current_streak)

    db.commit()
    db.refresh(habit)
    return habit
