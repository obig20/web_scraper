"""Timeline events within cases."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class EventType(str, enum.Enum):
    INCIDENT = "incident"
    DISCOVERY = "discovery"
    ARREST = "arrest"
    TRIAL = "trial"
    VERDICT = "verdict"
    SIGHTING = "sighting"
    REPORT = "report"
    DISAPPEARANCE = "disappearance"
    DEATH = "death"
    OTHER = "other"


class Event(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "events"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), default=EventType.OTHER)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    occurred_at_precision: Mapped[str] = mapped_column(String(20), default="day")
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id")
    )
    source_article_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id")
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    case = relationship("Case", back_populates="events")
    location = relationship("Location")
    timeline_entries = relationship("TimelineEntry", back_populates="event")
