"""Shared model mixins and association tables."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", UUID(as_uuid=True), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), primary_key=True),
)

case_tags = Table(
    "case_tags",
    Base.metadata,
    Column("case_id", UUID(as_uuid=True), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), primary_key=True),
)

article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", UUID(as_uuid=True), primary_key=True),
    Column("category_id", UUID(as_uuid=True), primary_key=True),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()
