import uuid
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.finance import (
    Credit,
    CreditPayment,
    SavingsGoal,
    SavingsTransaction,
    Transaction,
    TransactionType,
    Wallet,
)


class InsufficientFundsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно денег в кошельке для этой операции.",
        )


class InvalidAmountError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сумма должна быть больше нуля.",
        )


class FinanceService:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_wallet(self, user_id: uuid.UUID) -> Wallet:
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if wallet is None:
            wallet = Wallet(user_id=user_id)
            self.db.add(wallet)
            self.db.flush()
        return wallet

    def record_income(
        self, user_id: uuid.UUID, amount: Decimal, category_id: uuid.UUID | None,
        comment: str, date: datetime | None
    ) -> Transaction:
        if amount <= 0:
            raise InvalidAmountError()
        wallet = self._get_or_create_wallet(user_id)
        wallet.balance += amount
        wallet.updated_at = datetime.utcnow()
        tx = Transaction(
            user_id=user_id, amount=amount, type=TransactionType.income,
            category_id=category_id, comment=comment, date=date or datetime.utcnow(),
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def record_expense(
        self, user_id: uuid.UUID, amount: Decimal, category_id: uuid.UUID | None,
        comment: str, date: datetime | None
    ) -> Transaction:
        if amount <= 0:
            raise InvalidAmountError()
        wallet = self._get_or_create_wallet(user_id)
        if wallet.balance < amount:
            raise InsufficientFundsError()
        wallet.balance -= amount
        wallet.updated_at = datetime.utcnow()
        tx = Transaction(
            user_id=user_id, amount=amount, type=TransactionType.expense,
            category_id=category_id, comment=comment, date=date or datetime.utcnow(),
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def transfer_to_savings(self, user_id: uuid.UUID, goal: SavingsGoal, amount: Decimal) -> None:
        if amount <= 0:
            raise InvalidAmountError()
        wallet = self._get_or_create_wallet(user_id)
        if wallet.balance < amount:
            raise InsufficientFundsError()
        wallet.balance -= amount
        goal.saved_amount += amount
        self.db.add(SavingsTransaction(goal_id=goal.id, amount=amount))
        self.db.add(Transaction(
            user_id=user_id, amount=amount, type=TransactionType.transfer,
            comment=f"В копилку: {goal.name}", linked_savings_goal_id=goal.id,
            date=datetime.utcnow(),
        ))
        self.db.commit()

    def withdraw_from_savings(self, user_id: uuid.UUID, goal: SavingsGoal, amount: Decimal) -> None:
        if amount <= 0:
            raise InvalidAmountError()
        if goal.saved_amount < amount:
            raise InsufficientFundsError()
        wallet = self._get_or_create_wallet(user_id)
        wallet.balance += amount
        goal.saved_amount -= amount
        self.db.add(SavingsTransaction(goal_id=goal.id, amount=-amount))
        self.db.add(Transaction(
            user_id=user_id, amount=amount, type=TransactionType.income,
            comment=f"Из копилки: {goal.name}", linked_savings_goal_id=goal.id,
            date=datetime.utcnow(),
        ))
        self.db.commit()

    def pay_credit(self, user_id: uuid.UUID, credit: Credit, amount: Decimal) -> None:
        if amount <= 0:
            raise InvalidAmountError()
        wallet = self._get_or_create_wallet(user_id)
        if wallet.balance < amount:
            raise InsufficientFundsError()
        wallet.balance -= amount
        credit.remaining_amount = max(Decimal(0), credit.remaining_amount - amount)
        if credit.remaining_amount == 0:
            credit.is_closed = True
        self.db.add(CreditPayment(credit_id=credit.id, amount=amount))
        self.db.add(Transaction(
            user_id=user_id, amount=amount, type=TransactionType.expense,
            comment=f"Платёж по кредиту: {credit.name}", linked_credit_id=credit.id,
            date=datetime.utcnow(),
        ))
        self.db.commit()
