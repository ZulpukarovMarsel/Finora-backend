import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDPKMixin


class TransactionType(str, enum.Enum):
    income = "INCOME"
    expense = "EXPENSE"
    transfer = "TRANSFER"


class RecurrencePeriod(str, enum.Enum):
    monthly = "monthly"
    weekly = "weekly"
    yearly = "yearly"


class Wallet(UUIDPKMixin, Base):
    __tablename__ = "wallets"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    currency_code: Mapped[str] = mapped_column(String(8), default="KGS")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class TransactionCategory(UUIDPKMixin, Base):
    __tablename__ = "transaction_categories"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(80))
    icon_name: Mapped[str] = mapped_column(String(80))
    color_hex: Mapped[str] = mapped_column(String(8))
    kind: Mapped[TransactionType] = mapped_column(Enum(TransactionType, name="category_kind"))
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)


class Transaction(UUIDPKMixin, Base):
    __tablename__ = "transactions"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType, name="transaction_type"))
    category_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("transaction_categories.id"), nullable=True)
    comment: Mapped[str] = mapped_column(String(500), default="")
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    linked_savings_goal_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    linked_credit_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    category: Mapped["TransactionCategory | None"] = relationship()


class SavingsGoal(UUIDPKMixin, Base):
    __tablename__ = "savings_goals"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    target_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    saved_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    icon_name: Mapped[str] = mapped_column(String(80), default="gift.fill")
    color_hex: Mapped[str] = mapped_column(String(8), default="34E5FF")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    transactions: Mapped[list["SavingsTransaction"]] = relationship(
        back_populates="goal", cascade="all, delete-orphan"
    )


class SavingsTransaction(UUIDPKMixin, Base):
    __tablename__ = "savings_transactions"

    goal_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("savings_goals.id"))
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    goal: Mapped["SavingsGoal"] = relationship(back_populates="transactions")


class Credit(UUIDPKMixin, Base):
    __tablename__ = "credits"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    remaining_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    monthly_payment: Mapped[float] = mapped_column(Numeric(14, 2))
    interest_rate: Mapped[float] = mapped_column(Numeric(6, 2), default=0)
    payment_day: Mapped[int] = mapped_column(Integer, default=1)
    start_date: Mapped[date] = mapped_column(default=date.today)
    end_date: Mapped[date | None] = mapped_column(nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)

    payments: Mapped[list["CreditPayment"]] = relationship(
        back_populates="credit", cascade="all, delete-orphan"
    )


class CreditPayment(UUIDPKMixin, Base):
    __tablename__ = "credit_payments"

    credit_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("credits.id"))
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    credit: Mapped["Credit"] = relationship(back_populates="payments")


class RecurringExpense(UUIDPKMixin, Base):
    __tablename__ = "recurring_expenses"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    icon_name: Mapped[str] = mapped_column(String(80), default="house.fill")
    day_of_month: Mapped[int] = mapped_column(Integer)
    period: Mapped[RecurrencePeriod] = mapped_column(Enum(RecurrencePeriod, name="recurrence_period"), default=RecurrencePeriod.monthly)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_confirmed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
