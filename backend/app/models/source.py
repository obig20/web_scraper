"""Data source configuration and crawl metadata."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class SourceType(str, enum.Enum):
    NEWS = "news"
    GOVERNMENT = "government"
    POLICE = "police"
    COURT = "court"
    MISSING_PERSONS = "missing_persons"
    NEWSPAPER_ARCHIVE = "newspaper_archive"
    PUBLIC_DOMAIN_BOOK = "public_domain_book"
    FOLKLORE = "folklore"
    URBAN_LEGEND = "urban_legend"
    ACADEMIC = "academic"
    RSS = "rss"
    XML = "xml"
    API = "api"
    PODCAST = "podcast"
    YOUTUBE = "youtube"


class SourceStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"


class Source(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    base_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    credentials_encrypted: Mapped[str | None] = mapped_column(Text)
    status: Mapped[SourceStatus] = mapped_column(
        Enum(SourceStatus), default=SourceStatus.ACTIVE
    )
    credibility_base_score: Mapped[float] = mapped_column(Float, default=0.5)
    rate_limit: Mapped[float] = mapped_column(Float, default=2.0)
    use_proxy: Mapped[bool] = mapped_column(Boolean, default=False)
    respect_robots: Mapped[bool] = mapped_column(Boolean, default=True)
    last_crawled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    articles_count: Mapped[int] = mapped_column(Integer, default=0)
    crawl_schedule: Mapped[str | None] = mapped_column(String(64))
    is_incremental: Mapped[bool] = mapped_column(Boolean, default=True)

    articles = relationship("Article", back_populates="source", lazy="dynamic")
