import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.books import BookStatus


class BookCreate(BaseModel):
    title: str
    author: str = ""
    total_pages: int = 0
    status: BookStatus = BookStatus.wantToRead
    cover_image_url: str | None = None


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    total_pages: int | None = None
    current_page: int | None = None
    status: BookStatus | None = None
    cover_image_url: str | None = None


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    author: str
    cover_image_url: str | None
    total_pages: int
    current_page: int
    status: BookStatus
    start_date: date | None
    end_date: date | None
    rating: int | None
    would_recommend: bool | None
    created_at: datetime


class ReadingSessionStart(BaseModel):
    pass


class ReadingSessionEnd(BaseModel):
    end_page: int
    recap: str = ""
    main_idea: str = ""
    personal_thought: str = ""


class ReadingSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    book_id: uuid.UUID
    start_time: datetime
    end_time: datetime | None
    start_page: int
    end_page: int
    recap: str
    main_idea: str
    personal_thought: str


class BookChapterCreate(BaseModel):
    title: str
    page_range_start: int
    page_range_end: int
    recap: str = ""
    what_i_learned: str = ""
    key_takeaway: str = ""
    thoughts: str = ""


class BookChapterRead(BookChapterCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    book_id: uuid.UUID


class BookSummaryCreate(BaseModel):
    recap: str = ""
    key_takeaway: str = ""
    what_i_learned: str = ""
    what_i_will_apply: str = ""
    rating: int = 5
    would_recommend: bool = True


class BookSummaryRead(BookSummaryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    book_id: uuid.UUID
    created_at: datetime
