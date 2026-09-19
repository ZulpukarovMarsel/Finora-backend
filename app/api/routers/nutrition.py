import uuid
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.water_nutrition import FoodItem
from app.schemas.water_nutrition import FoodItemCreate, FoodItemRead

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


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
