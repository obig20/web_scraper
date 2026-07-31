"""People involved in cases (victims, suspects, witnesses, etc.)."""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class PersonRole(str, enum.Enum):
    VICTIM = "victim"
    SUSPECT = "suspect"
    WITNESS = "witness"
    DETECTIVE = "detective"
    OFFICIAL = "official"
    FAMILY = "family"
    REPORTER = "reporter"
    OTHER = "other"


class Person(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "people"

    name: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    aliases: Mapped[list[str] | None] = mapped_column(JSONB, default=list)
    role: Mapped[PersonRole] = mapped_column(Enum(PersonRole), default=PersonRole.OTHER)
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), index=True
    )
    article_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id")
    )
    description: Mapped[str | None] = mapped_column(Text)
    birth_date: Mapped[str | None] = mapped_column(String(32))
    death_date: Mapped[str | None] = mapped_column(String(32))
    nationality: Mapped[str | None] = mapped_column(String(2))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    case = relationship("Case", backref="people")
