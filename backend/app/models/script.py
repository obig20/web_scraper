"""Story scripts and AI-generated research notes."""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class ScriptStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"


class Script(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "scripts"

    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ScriptStatus] = mapped_column(Enum(ScriptStatus), default=ScriptStatus.DRAFT)
    version: Mapped[int] = mapped_column(default=1)
    source_article_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    case = relationship("Case", back_populates="scripts")


class ResearchNote(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "research_notes"

    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), index=True
    )
    article_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    timeline: Mapped[list] = mapped_column(JSONB, default=list)
    people_involved: Mapped[list] = mapped_column(JSONB, default=list)
    important_facts: Mapped[list] = mapped_column(JSONB, default=list)
    contradictions: Mapped[list] = mapped_column(JSONB, default=list)
    interesting_details: Mapped[list] = mapped_column(JSONB, default=list)
    open_questions: Mapped[list] = mapped_column(JSONB, default=list)
    related_cases: Mapped[list] = mapped_column(JSONB, default=list)
    storytelling_angles: Mapped[list] = mapped_column(JSONB, default=list)
    thumbnail_ideas: Mapped[list] = mapped_column(JSONB, default=list)
    potential_titles: Mapped[list] = mapped_column(JSONB, default=list)
    source_citations: Mapped[list] = mapped_column(JSONB, default=list)

    case = relationship("Case", back_populates="research_notes")
