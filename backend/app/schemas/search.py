"""Search schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import SearchFilters


class SearchQuery(SearchFilters):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "published_at"
    sort_order: str = "desc"


class SearchHit(BaseModel):
    id: str
    article_id: UUID | None = None
    case_id: UUID | None = None
    title: str
    summary: str | None
    score: float
    crime_types: list[str] = Field(default_factory=list)
    horror_categories: list[str] = Field(default_factory=list)
    country: str | None = None
    published_at: datetime | None = None
    highlight: dict | None = None


class SearchResult(BaseModel):
    hits: list[SearchHit]
    total: int
    page: int
    page_size: int
    took_ms: float
    aggregations: dict | None = None
