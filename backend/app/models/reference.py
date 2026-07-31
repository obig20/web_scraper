"""Source citations linking articles to original publications."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Reference(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "references"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False, index=True
    )
    citation_text: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str | None] = mapped_column(String(2048))
    publisher: Mapped[str | None] = mapped_column(String(512))
    published_date: Mapped[str | None] = mapped_column(String(32))
    access_date: Mapped[str | None] = mapped_column(String(32))

    article = relationship("Article", back_populates="references")
