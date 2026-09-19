from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.gamification import DailySummary, XPRecord
from app.models.user import User
from app.schemas.gamification import DailySummaryRead, DailySummaryUpdate, XPAward, XPRecordRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/profile", response_model=UserRead)
def get_profile(user: User = Depends(get_current_user)):
    return user


@router.post("/xp", response_model=UserRead)
def award_xp(payload: XPAward, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.total_xp += payload.amount
    db.add(XPRecord(user_id=user.id, amount=payload.amount, source=payload.source, note=payload.note))

    summary = _get_or_create_summary(db, user, date.today())
    summary.xp_earned += payload.amount

    db.commit()
    db.refresh(user)
    return user


@router.get("/xp/history", response_model=list[XPRecordRead])
def xp_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(XPRecord).filter(XPRecord.user_id == user.id).order_by(XPRecord.date.desc()).limit(200).all()


def _get_or_create_summary(db: Session, user: User, target_date: date) -> DailySummary:
    summary = db.query(DailySummary).filter(DailySummary.user_id == user.id, DailySummary.date == target_date).first()
    if not summary:
        summary = DailySummary(user_id=user.id, date=target_date)
        db.add(summary)
        db.flush()
    return summary


@router.get("/summary/today", response_model=DailySummaryRead)
def today_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    summary = _get_or_create_summary(db, user, date.today())
    db.commit()
    db.refresh(summary)
    return summary


@router.patch("/summary/today", response_model=DailySummaryRead)
def update_today_summary(payload: DailySummaryUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    summary = _get_or_create_summary(db, user, date.today())
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(summary, field, value)
    db.commit()
    db.refresh(summary)
    return summary
