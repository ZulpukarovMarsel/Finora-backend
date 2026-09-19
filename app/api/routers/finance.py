import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.finance import Transaction, TransactionCategory, TransactionType, Wallet
from app.models.user import User
from app.schemas.finance import (
    CategoryCreate,
    CategoryRead,
    TransactionCreate,
    TransactionRead,
    WalletRead,
)
from app.services.finance_service import FinanceService

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/wallet", response_model=WalletRead)
def get_wallet(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet:
        wallet = Wallet(user_id=user.id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(
    kind: TransactionType | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(TransactionCategory).filter(TransactionCategory.user_id == user.id)
    if kind:
        query = query.filter(TransactionCategory.kind == kind)
    return query.order_by(TransactionCategory.name).all()


@router.post("/categories", response_model=CategoryRead, status_code=201)
def create_category(
    payload: CategoryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    category = TransactionCategory(user_id=user.id, is_custom=True, **payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/transactions", response_model=list[TransactionRead])
def list_transactions(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Transaction).filter(Transaction.user_id == user.id)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)
    return query.order_by(Transaction.date.desc()).all()


@router.post("/transactions", response_model=TransactionRead, status_code=201)
def create_transaction(
    payload: TransactionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    service = FinanceService(db)
    if payload.type == TransactionType.income:
        return service.record_income(user.id, payload.amount, payload.category_id, payload.comment, payload.date)
    if payload.type == TransactionType.expense:
        return service.record_expense(user.id, payload.amount, payload.category_id, payload.comment, payload.date)
    raise HTTPException(
        status_code=400,
        detail="Переводы создаются через /savings/{goal_id}/deposit или /credits/{credit_id}/pay",
    )
