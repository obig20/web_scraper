"""Case records grouping related articles and events."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin, case_tags


class CaseStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    COLD = "cold"
    UNSOLVED = "unsolved"
    LEGEND = "legend"
    DISPUTED = "disputed"


class Case(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cases"

    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.OPEN)
    crime_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    horror_categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    country: Mapped[str | None] = mapped_column(String(2), index=True)
    primary_location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id")
    )
    date_started: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_ended: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    confidence_score: Mapped[float | None] = mapped_column(Float)
    story_potential_score: Mapped[float | None] = mapped_column(Float)
    cluster_id: Mapped[int | None] = mapped_column(index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    articles = relationship("Article", back_populates="case")
    events = relationship("Event", back_populates="case")
    timeline_entries = relationship("TimelineEntry", back_populates="case")
    evidence = relationship("Evidence", back_populates="case")
    scripts = relationship("Script", back_populates="case")
    research_notes = relationship("ResearchNote", back_populates="case")
    tags = relationship("Tag", secondary=case_tags, backref="cases")
