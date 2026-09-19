import uuid
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.learning import LearningGoal, LearningSession, MathExerciseRecord, Word
from app.models.user import User
from app.schemas.learning import (
    LearningGoalCreate,
    LearningGoalRead,
    LearningSessionCreate,
    LearningSessionRead,
    MathExerciseCreate,
    MathExerciseRead,
    WordCreate,
    WordRead,
    WordReview,
)

router = APIRouter(prefix="/learning", tags=["learning"])


# --- Goals -----------------------------------------------------------------

@router.get("/goals", response_model=list[LearningGoalRead])
def list_goals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(LearningGoal).filter(LearningGoal.user_id == user.id).order_by(LearningGoal.created_at.desc()).all()


@router.post("/goals", response_model=LearningGoalRead, status_code=201)
def create_goal(payload: LearningGoalCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = LearningGoal(user_id=user.id, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.post("/goals/{goal_id}/sessions", response_model=LearningSessionRead, status_code=201)
def log_session(goal_id: uuid.UUID, payload: LearningSessionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = db.query(LearningGoal).filter(LearningGoal.id == goal_id, LearningGoal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    session = LearningSession(goal_id=goal.id, **payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# --- German flashcards -------------------------------------------------------

@router.get("/words", response_model=list[WordRead])
def list_words(language_code: str = "de", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Word)
        .filter(Word.user_id == user.id, Word.language_code == language_code)
        .order_by(Word.created_at)
        .all()
    )


@router.post("/words", response_model=WordRead, status_code=201)
def add_word(payload: WordCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    word = Word(user_id=user.id, **payload.model_dump())
    db.add(word)
    db.commit()
    db.refresh(word)
    return word


@router.post("/words/{word_id}/review", response_model=WordRead)
def review_word(word_id: uuid.UUID, payload: WordReview, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    word = db.query(Word).filter(Word.id == word_id, Word.user_id == user.id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Слово не найдено")
    word.is_learned = payload.is_learned
    word.last_reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(word)
    return word


# --- Math --------------------------------------------------------------------

@router.post("/math", response_model=MathExerciseRead, status_code=201)
def log_math_exercise(payload: MathExerciseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = MathExerciseRecord(user_id=user.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/math/stats")
def math_stats(on_date: date | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    target = on_date or date.today()
    start = datetime.combine(target, datetime.min.time())
    end = start + timedelta(days=1)
    records = (
        db.query(MathExerciseRecord)
        .filter(MathExerciseRecord.user_id == user.id, MathExerciseRecord.date >= start, MathExerciseRecord.date < end)
        .all()
    )
    correct = sum(1 for r in records if r.is_correct)
    return {"correct": correct, "total": len(records)}
