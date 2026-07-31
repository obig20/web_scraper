"""Article schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.article import ProcessingStatus
from app.schemas.common import ORMBase


class ArticleCreate(BaseModel):
    source_id: UUID
    url: str
    title: str
    content: str
    author: str | None = None
    published_at: datetime | None = None
    external_id: str | None = None


class ArticleSummary(ORMBase):
    id: UUID
    title: str
    url: str
    summary: str | None
    published_at: datetime | None
    crime_types: list[str]
    horror_categories: list[str]
    credibility_score: float | None
    story_potential_score: float | None
    processing_status: ProcessingStatus


class ArticleRead(ArticleSummary):
    source_id: UUID
    case_id: UUID | None
    content: str
    keywords: list[str]
    sentiment_score: float | None
    confidence_score: float | None
    country: str | None
    entities: dict
    is_duplicate: bool
    word_count: int
    fetched_at: datetime
