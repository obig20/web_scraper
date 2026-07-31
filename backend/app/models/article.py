"""Collected articles and extracted content."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin, article_categories, article_tags


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DUPLICATE = "duplicate"


class Article(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "articles"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), index=True
    )
    external_id: Mapped[str | None] = mapped_column(String(512), index=True)
    url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    simhash: Mapped[str | None] = mapped_column(String(32), index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(512))
    language: Mapped[str] = mapped_column(String(10), default="en")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus), default=ProcessingStatus.PENDING, index=True
    )
    crime_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    horror_categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    keywords: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    sentiment_score: Mapped[float | None] = mapped_column(Float)
    credibility_score: Mapped[float | None] = mapped_column(Float)
    story_potential_score: Mapped[float | None] = mapped_column(Float)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    country: Mapped[str | None] = mapped_column(String(2), index=True)
    entities: Mapped[dict] = mapped_column(JSONB, default=dict)
    ai_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    embedding_id: Mapped[str | None] = mapped_column(String(64))
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    source = relationship("Source", back_populates="articles")
    case = relationship("Case", back_populates="articles")
    references = relationship("Reference", back_populates="article")
    media = relationship("Media", back_populates="article")
    tags = relationship("Tag", secondary=article_tags, backref="articles")
    categories = relationship("Category", secondary=article_categories, backref="articles")
