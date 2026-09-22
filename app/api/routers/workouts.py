import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.workouts import WorkoutCompletion, WorkoutExercise, WorkoutPlan, WorkoutSettings
from app.schemas.workouts import (
    WorkoutCompletionCreate,
    WorkoutCompletionRead,
    WorkoutExerciseCreate,
    WorkoutExerciseRead,
    WorkoutPlanCreate,
    WorkoutPlanRead,
    WorkoutSettingsRead,
    WorkoutSettingsUpdate,
)

router = APIRouter(prefix="/workouts", tags=["workouts"])


def _get_or_create_settings(db: Session, user: User) -> WorkoutSettings:
    settings = db.query(WorkoutSettings).filter(WorkoutSettings.user_id == user.id).first()
    if not settings:
        settings = WorkoutSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/settings", response_model=WorkoutSettingsRead)
def get_settings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_or_create_settings(db, user)


@router.put("/settings", response_model=WorkoutSettingsRead)
def update_settings(payload: WorkoutSettingsUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    settings = _get_or_create_settings(db, user)
    settings.default_rest_seconds = payload.default_rest_seconds
    settings.target_total_minutes = payload.target_total_minutes
    db.commit()
    db.refresh(settings)
    return settings


def _get_owned_plan(db: Session, user: User, plan_id: uuid.UUID) -> WorkoutPlan:
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    return plan


@router.get("/plans", response_model=list[WorkoutPlanRead])
def list_plans(weekday: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plans = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user.id).order_by(WorkoutPlan.created_at).all()
    if weekday is not None:
        plans = [p for p in plans if weekday in p.weekdays]
    return plans


@router.post("/plans", response_model=WorkoutPlanRead, status_code=201)
def create_plan(payload: WorkoutPlanCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = payload.model_dump()
    exercises_data = data.pop("exercises")
    plan = WorkoutPlan(user_id=user.id, **data)
    db.add(plan)
    db.flush()
    for index, exercise_data in enumerate(exercises_data):
        exercise_data.setdefault("order_index", index)
        db.add(WorkoutExercise(plan_id=plan.id, **exercise_data))
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/plans/{plan_id}/exercises", response_model=WorkoutExerciseRead, status_code=201)
def add_exercise(plan_id: uuid.UUID, payload: WorkoutExerciseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plan = _get_owned_plan(db, user, plan_id)
    exercise = WorkoutExercise(plan_id=plan.id, **payload.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.delete("/plans/{plan_id}", status_code=204)
def delete_plan(plan_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plan = _get_owned_plan(db, user, plan_id)
    db.delete(plan)
    db.commit()


@router.get("/plans/{plan_id}/completed-today")
def is_completed_today(plan_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plan = _get_owned_plan(db, user, plan_id)
    exists = (
        db.query(WorkoutCompletion)
        .filter(WorkoutCompletion.plan_id == plan.id, WorkoutCompletion.date == date.today())
        .first()
        is not None
    )
    return {"completed": exists}


@router.post("/plans/{plan_id}/complete", response_model=WorkoutCompletionRead, status_code=201)
def record_completion(
    plan_id: uuid.UUID, payload: WorkoutCompletionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    plan = _get_owned_plan(db, user, plan_id)
    completion = WorkoutCompletion(user_id=user.id, plan_id=plan.id, **payload.model_dump())
    db.add(completion)
    db.commit()
    db.refresh(completion)
    return completion
