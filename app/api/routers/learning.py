import uuid
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.learning import LearningGoal, LearningSession, MathExerciseRecord, StudyLanguage, Word
from app.models.user import User
from app.schemas.learning import (
    LearningGoalCreate,
    LearningGoalRead,
    LearningSessionCreate,
    LearningSessionRead,
    MathExerciseCreate,
    MathExerciseRead,
    StudyLanguageCreate,
    StudyLanguageRead,
    WordAnswer,
    WordCreate,
    WordRead,
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


# --- Study languages ---------------------------------------------------------
# Replaces the old hardcoded "German flashcards" (language_code="de") with
# the client's "Языки" feature: the user adds any language they want, then
# builds a word/translation dictionary inside it.

def _get_owned_language(db: Session, user: User, language_id: uuid.UUID) -> StudyLanguage:
    language = db.query(StudyLanguage).filter(StudyLanguage.id == language_id, StudyLanguage.user_id == user.id).first()
    if not language:
        raise HTTPException(status_code=404, detail="Язык не найден")
    return language


@router.get("/languages", response_model=list[StudyLanguageRead])
def list_languages(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(StudyLanguage).filter(StudyLanguage.user_id == user.id).order_by(StudyLanguage.created_at).all()


@router.post("/languages", response_model=StudyLanguageRead, status_code=201)
def add_language(payload: StudyLanguageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    language = StudyLanguage(user_id=user.id, **payload.model_dump())
    db.add(language)
    db.commit()
    db.refresh(language)
    return language


@router.delete("/languages/{language_id}", status_code=204)
def delete_language(language_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    language = _get_owned_language(db, user, language_id)
    db.delete(language)
    db.commit()


# --- Words -------------------------------------------------------------------

@router.get("/languages/{language_id}/words", response_model=list[WordRead])
def list_words(language_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_owned_language(db, user, language_id)
    return (
        db.query(Word)
        .filter(Word.user_id == user.id, Word.language_id == language_id)
        .order_by(Word.created_at)
        .all()
    )


@router.get("/words", response_model=list[WordRead])
def list_all_words(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """All words across every language — used by the "общий тест по всем
    языкам" (test across all languages) mode."""
    return db.query(Word).filter(Word.user_id == user.id).order_by(Word.created_at).all()


@router.post("/languages/{language_id}/words", response_model=WordRead, status_code=201)
def add_word(language_id: uuid.UUID, payload: WordCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_owned_language(db, user, language_id)
    word = Word(user_id=user.id, language_id=language_id, **payload.model_dump())
    db.add(word)
    db.commit()
    db.refresh(word)
    return word


@router.post("/words/{word_id}/answer", response_model=WordRead)
def answer_word(word_id: uuid.UUID, payload: WordAnswer, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    word = db.query(Word).filter(Word.id == word_id, Word.user_id == user.id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Слово не найдено")
    word.last_reviewed_at = datetime.utcnow()
    if payload.correct:
        word.is_learned = True
        word.needs_review = False
    else:
        word.miss_count += 1
        word.needs_review = True
    db.commit()
    db.refresh(word)
    return word


@router.get("/words/needing-review", response_model=list[WordRead])
def words_needing_review(
    language_id: uuid.UUID | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    query = db.query(Word).filter(Word.user_id == user.id, Word.needs_review.is_(True))
    if language_id:
        query = query.filter(Word.language_id == language_id)
    return query.all()


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
