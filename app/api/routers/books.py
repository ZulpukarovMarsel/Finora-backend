import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.books import Book, BookChapter, BookStatus, BookSummary, ReadingSession
from app.models.user import User
from app.schemas.books import (
    BookChapterCreate,
    BookChapterRead,
    BookCreate,
    BookRead,
    BookSummaryCreate,
    BookSummaryRead,
    BookUpdate,
    ReadingSessionEnd,
    ReadingSessionRead,
)

router = APIRouter(prefix="/books", tags=["books"])


def _get_owned_book(db: Session, user: User, book_id: uuid.UUID) -> Book:
    book = db.query(Book).filter(Book.id == book_id, Book.user_id == user.id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book


@router.get("", response_model=list[BookRead])
def list_books(status_filter: BookStatus | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(Book).filter(Book.user_id == user.id)
    if status_filter:
        query = query.filter(Book.status == status_filter)
    return query.order_by(Book.created_at.desc()).all()


@router.post("", response_model=BookRead, status_code=201)
def create_book(payload: BookCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = Book(user_id=user.id, **payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.patch("/{book_id}", response_model=BookRead)
def update_book(book_id: uuid.UUID, payload: BookUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = _get_owned_book(db, user, book_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = _get_owned_book(db, user, book_id)
    db.delete(book)
    db.commit()


@router.post("/{book_id}/sessions/start", response_model=ReadingSessionRead, status_code=201)
def start_session(book_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = _get_owned_book(db, user, book_id)
    session = ReadingSession(book_id=book.id, start_page=book.current_page, end_page=book.current_page)
    db.add(session)
    if book.status == BookStatus.wantToRead:
        book.status = BookStatus.reading
        book.start_date = datetime.utcnow().date()
    db.commit()
    db.refresh(session)
    return session


@router.post("/{book_id}/sessions/{session_id}/end", response_model=ReadingSessionRead)
def end_session(
    book_id: uuid.UUID, session_id: uuid.UUID, payload: ReadingSessionEnd,
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    book = _get_owned_book(db, user, book_id)
    session = db.query(ReadingSession).filter(ReadingSession.id == session_id, ReadingSession.book_id == book.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия чтения не найдена")

    session.end_time = datetime.utcnow()
    session.end_page = payload.end_page
    session.recap = payload.recap
    session.main_idea = payload.main_idea
    session.personal_thought = payload.personal_thought

    book.current_page = min(payload.end_page, book.total_pages) if book.total_pages else payload.end_page

    db.commit()
    db.refresh(session)
    return session


@router.get("/{book_id}/sessions", response_model=list[ReadingSessionRead])
def list_sessions(book_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = _get_owned_book(db, user, book_id)
    return db.query(ReadingSession).filter(ReadingSession.book_id == book.id).order_by(ReadingSession.start_time.desc()).all()


@router.post("/{book_id}/chapters", response_model=BookChapterRead, status_code=201)
def add_chapter(book_id: uuid.UUID, payload: BookChapterCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = _get_owned_book(db, user, book_id)
    chapter = BookChapter(book_id=book.id, **payload.model_dump())
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/{book_id}/chapters", response_model=list[BookChapterRead])
def list_chapters(book_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = _get_owned_book(db, user, book_id)
    return db.query(BookChapter).filter(BookChapter.book_id == book.id).order_by(BookChapter.page_range_start).all()


@router.post("/{book_id}/finish", response_model=BookSummaryRead)
def finish_book(book_id: uuid.UUID, payload: BookSummaryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = _get_owned_book(db, user, book_id)
    book.status = BookStatus.finished
    book.end_date = datetime.utcnow().date()
    book.current_page = book.total_pages
    book.rating = payload.rating
    book.would_recommend = payload.would_recommend

    summary = db.query(BookSummary).filter(BookSummary.book_id == book.id).first()
    if summary:
        for field, value in payload.model_dump().items():
            setattr(summary, field, value)
    else:
        summary = BookSummary(book_id=book.id, **payload.model_dump())
        db.add(summary)

    db.commit()
    db.refresh(summary)
    return summary
