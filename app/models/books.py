import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDPKMixin


class BookStatus(str, enum.Enum):
    wantToRead = "wantToRead"
    reading = "reading"
    finished = "finished"
    onHold = "onHold"


class Book(UUIDPKMixin, Base):
    __tablename__ = "books"

    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    author: Mapped[str] = mapped_column(String(200), default="")
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total_pages: Mapped[int] = mapped_column(Integer, default=0)
    current_page: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[BookStatus] = mapped_column(Enum(BookStatus, name="book_status"), default=BookStatus.wantToRead)
    start_date: Mapped[date | None] = mapped_column(nullable=True)
    end_date: Mapped[date | None] = mapped_column(nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    would_recommend: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    sessions: Mapped[list["ReadingSession"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    chapters: Mapped[list["BookChapter"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    notes: Mapped[list["BookNote"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    summary: Mapped["BookSummary | None"] = relationship(back_populates="book", uselist=False, cascade="all, delete-orphan")


class ReadingSession(UUIDPKMixin, Base):
    __tablename__ = "reading_sessions"

    book_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("books.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    start_page: Mapped[int] = mapped_column(Integer, default=0)
    end_page: Mapped[int] = mapped_column(Integer, default=0)
    recap: Mapped[str] = mapped_column(String(2000), default="")
    main_idea: Mapped[str] = mapped_column(String(2000), default="")
    personal_thought: Mapped[str] = mapped_column(String(2000), default="")

    book: Mapped["Book"] = relationship(back_populates="sessions")


class BookChapter(UUIDPKMixin, Base):
    __tablename__ = "book_chapters"

    book_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("books.id"))
    title: Mapped[str] = mapped_column(String(300))
    page_range_start: Mapped[int] = mapped_column(Integer, default=0)
    page_range_end: Mapped[int] = mapped_column(Integer, default=0)
    recap: Mapped[str] = mapped_column(String(2000), default="")
    what_i_learned: Mapped[str] = mapped_column(String(2000), default="")
    key_takeaway: Mapped[str] = mapped_column(String(2000), default="")
    thoughts: Mapped[str] = mapped_column(String(2000), default="")

    book: Mapped["Book"] = relationship(back_populates="chapters")


class BookNote(UUIDPKMixin, Base):
    __tablename__ = "book_notes"

    book_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("books.id"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    recap: Mapped[str] = mapped_column(String(2000), default="")
    main_idea: Mapped[str] = mapped_column(String(2000), default="")
    personal_thought: Mapped[str] = mapped_column(String(2000), default="")

    book: Mapped["Book"] = relationship(back_populates="notes")


class BookSummary(UUIDPKMixin, Base):
    __tablename__ = "book_summaries"

    book_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("books.id"), unique=True)
    recap: Mapped[str] = mapped_column(String(2000), default="")
    key_takeaway: Mapped[str] = mapped_column(String(2000), default="")
    what_i_learned: Mapped[str] = mapped_column(String(2000), default="")
    what_i_will_apply: Mapped[str] = mapped_column(String(2000), default="")
    rating: Mapped[int] = mapped_column(Integer, default=5)
    would_recommend: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    book: Mapped["Book"] = relationship(back_populates="summary")
