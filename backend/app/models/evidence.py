"""Physical and digital evidence records."""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class EvidenceType(str, enum.Enum):
    PHYSICAL = "physical"
    DIGITAL = "digital"
    DOCUMENT = "document"
    TESTIMONY = "testimony"
    FORENSIC = "forensic"
    OTHER = "other"


class Evidence(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "evidence"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType), default=EvidenceType.OTHER
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source_article_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id")
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    case = relationship("Case", back_populates="evidence")
