"""Geographic locations with optional coordinates."""

import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Location(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "locations"

    name: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    location_type: Mapped[str | None] = mapped_column(String(64))
    address: Mapped[str | None] = mapped_column(String(1024))
    city: Mapped[str | None] = mapped_column(String(256), index=True)
    region: Mapped[str | None] = mapped_column(String(256))
    country: Mapped[str | None] = mapped_column(String(2), index=True)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), index=True
    )
    article_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id")
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
