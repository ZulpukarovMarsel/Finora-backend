import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.finance import RecurringExpense
from app.models.user import User
from app.schemas.finance import RecurringExpenseCreate, RecurringExpenseRead
from app.services.finance_service import FinanceService

router = APIRouter(prefix="/recurring-expenses", tags=["recurring-expenses"])


@router.get("", response_model=list[RecurringExpenseRead])
def list_recurring(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(RecurringExpense)
        .filter(RecurringExpense.user_id == user.id)
        .order_by(RecurringExpense.day_of_month)
        .all()
    )


@router.post("", response_model=RecurringExpenseRead, status_code=201)
def create_recurring(payload: RecurringExpenseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    expense = RecurringExpense(user_id=user.id, **payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.post("/{expense_id}/confirm", response_model=RecurringExpenseRead)
def confirm_payment(expense_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    expense = db.query(RecurringExpense).filter(
        RecurringExpense.id == expense_id, RecurringExpense.user_id == user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Расход не найден")

    FinanceService(db).record_expense(user.id, expense.amount, None, expense.name, None)
    expense.last_confirmed_date = datetime.utcnow()
    db.commit()
    db.refresh(expense)
    return expense
