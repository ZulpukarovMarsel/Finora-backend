import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.finance import Credit
from app.models.user import User
from app.schemas.finance import AmountRequest, CreditCreate, CreditRead
from app.services.finance_service import FinanceService

router = APIRouter(prefix="/credits", tags=["credits"])


def _get_owned_credit(db: Session, user: User, credit_id: uuid.UUID) -> Credit:
    credit = db.query(Credit).filter(Credit.id == credit_id, Credit.user_id == user.id).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Кредит не найден")
    return credit


@router.get("", response_model=list[CreditRead])
def list_credits(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Credit).filter(Credit.user_id == user.id).order_by(Credit.start_date.desc()).all()


@router.post("", response_model=CreditRead, status_code=201)
def create_credit(payload: CreditCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = payload.model_dump()
    credit = Credit(user_id=user.id, **{k: v for k, v in data.items() if v is not None})
    db.add(credit)
    db.commit()
    db.refresh(credit)
    return credit


@router.post("/{credit_id}/pay", response_model=CreditRead)
def pay_credit(credit_id: uuid.UUID, payload: AmountRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    credit = _get_owned_credit(db, user, credit_id)
    FinanceService(db).pay_credit(user.id, credit, payload.amount)
    db.refresh(credit)
    return credit


@router.post("/{credit_id}/close", response_model=CreditRead)
def close_credit_in_full(credit_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    credit = _get_owned_credit(db, user, credit_id)
    if credit.remaining_amount > 0:
        FinanceService(db).pay_credit(user.id, credit, credit.remaining_amount)
        db.refresh(credit)
    return credit
