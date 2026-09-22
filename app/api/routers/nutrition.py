import uuid
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.water_nutrition import FoodItem, NutritionGoal
from app.schemas.water_nutrition import FoodItemCreate, FoodItemRead, NutritionGoalRead, NutritionGoalUpdate

router = APIRouter(prefix="/nutrition", tags=["nutrition"])

def _get_or_create_goal(db: Session, user: User) -> NutritionGoal:
    goal = db.query(NutritionGoal).filter(NutritionGoal.user_id == user.id).first()
    if not goal:
        goal = NutritionGoal(user_id=user.id)
        db.add(goal)
        db.commit()
        db.refresh(goal)
    return goal


@router.get("/goal", response_model=NutritionGoalRead)
def get_goal(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_or_create_goal(db, user)


@router.put("/goal", response_model=NutritionGoalRead)
def update_goal(payload: NutritionGoalUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = _get_or_create_goal(db, user)
    goal.daily_calorie_goal = payload.daily_calorie_goal
    goal.protein_goal_grams = payload.protein_goal_grams
    goal.fat_goal_grams = payload.fat_goal_grams
    goal.carb_goal_grams = payload.carb_goal_grams
    goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/food", response_model=list[FoodItemRead])
def list_food(on_date: date | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    target = on_date or date.today()
    start = datetime.combine(target, datetime.min.time())
    end = start + timedelta(days=1)
    return (
        db.query(FoodItem)
        .filter(FoodItem.user_id == user.id, FoodItem.date >= start, FoodItem.date < end)
        .order_by(FoodItem.date)
        .all()
    )


@router.post("/food", response_model=FoodItemRead, status_code=201)
def add_food(payload: FoodItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = FoodItem(user_id=user.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/food/{item_id}", status_code=204)
def delete_food(item_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(FoodItem).filter(FoodItem.id == item_id, FoodItem.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    db.delete(item)
    db.commit()
