import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.finance import RecurrencePeriod, TransactionType


class WalletRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    balance: Decimal
    currency_code: str
    updated_at: datetime


class CategoryCreate(BaseModel):
    name: str
    icon_name: str
    color_hex: str
    kind: TransactionType


class CategoryRead(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    is_custom: bool


class TransactionCreate(BaseModel):
    amount: Decimal
    type: TransactionType
    category_id: uuid.UUID | None = None
    comment: str = ""
    date: datetime | None = None


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    amount: Decimal
    type: TransactionType
    category_id: uuid.UUID | None
    comment: str
    date: datetime
    created_at: datetime
    linked_savings_goal_id: uuid.UUID | None
    linked_credit_id: uuid.UUID | None


class SavingsGoalCreate(BaseModel):
    name: str
    target_amount: Decimal
    icon_name: str = "gift.fill"
    color_hex: str = "34E5FF"


class SavingsGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    target_amount: Decimal
    saved_amount: Decimal
    icon_name: str
    color_hex: str
    created_at: datetime
    is_archived: bool


class AmountRequest(BaseModel):
    amount: Decimal


class CreditCreate(BaseModel):
    name: str
    total_amount: Decimal
    remaining_amount: Decimal
    monthly_payment: Decimal
    interest_rate: Decimal = Decimal(0)
    payment_day: int = 1
    start_date: date | None = None
    end_date: date | None = None


class CreditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    total_amount: Decimal
    remaining_amount: Decimal
    monthly_payment: Decimal
    interest_rate: Decimal
    payment_day: int
    start_date: date
    end_date: date | None
    is_closed: bool


class RecurringExpenseCreate(BaseModel):
    name: str
    amount: Decimal
    icon_name: str = "house.fill"
    day_of_month: int
    period: RecurrencePeriod = RecurrencePeriod.monthly


class RecurringExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    amount: Decimal
    icon_name: str
    day_of_month: int
    period: RecurrencePeriod
    is_active: bool
    last_confirmed_date: datetime | None
