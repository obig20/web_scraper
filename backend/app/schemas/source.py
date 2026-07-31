"""Source schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.models.source import SourceStatus, SourceType
from app.schemas.common import ORMBase


class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    source_type: SourceType
    base_url: HttpUrl | str
    description: str | None = None
    config: dict = Field(default_factory=dict)
    credibility_base_score: float = Field(default=0.5, ge=0, le=1)
    rate_limit: float = Field(default=2.0, gt=0)
    crawl_schedule: str | None = None


class SourceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    config: dict | None = None
    status: SourceStatus | None = None
    rate_limit: float | None = None
    crawl_schedule: str | None = None


class SourceRead(ORMBase):
    id: UUID
    name: str
    slug: str
    source_type: SourceType
    base_url: str
    description: str | None
    config: dict
    status: SourceStatus
    credibility_base_score: float
    rate_limit: float
    last_crawled_at: datetime | None
    last_success_at: datetime | None
    articles_count: int
    crawl_schedule: str | None
