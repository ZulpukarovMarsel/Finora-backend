import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.finance import SavingsGoal
from app.models.user import User
from app.schemas.finance import AmountRequest, SavingsGoalCreate, SavingsGoalRead
from app.services.finance_service import FinanceService

router = APIRouter(prefix="/savings", tags=["savings"])


def _get_owned_goal(db: Session, user: User, goal_id: uuid.UUID) -> SavingsGoal:
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Копилка не найдена")
    return goal


@router.get("", response_model=list[SavingsGoalRead])
def list_goals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(SavingsGoal)
        .filter(SavingsGoal.user_id == user.id, SavingsGoal.is_archived.is_(False))
        .order_by(SavingsGoal.created_at.desc())
        .all()
    )


@router.post("", response_model=SavingsGoalRead, status_code=201)
def create_goal(payload: SavingsGoalCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = SavingsGoal(user_id=user.id, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.post("/{goal_id}/deposit", response_model=SavingsGoalRead)
def deposit(goal_id: uuid.UUID, payload: AmountRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = _get_owned_goal(db, user, goal_id)
    FinanceService(db).transfer_to_savings(user.id, goal, payload.amount)
    db.refresh(goal)
    return goal


@router.post("/{goal_id}/withdraw", response_model=SavingsGoalRead)
def withdraw(goal_id: uuid.UUID, payload: AmountRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = _get_owned_goal(db, user, goal_id)
    FinanceService(db).withdraw_from_savings(user.id, goal, payload.amount)
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = _get_owned_goal(db, user, goal_id)
    db.delete(goal)
    db.commit()
