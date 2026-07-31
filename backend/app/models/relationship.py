"""Entity relationship graph edges."""

import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class EntityType(str, enum.Enum):
    PERSON = "person"
    CASE = "case"
    LOCATION = "location"
    ORGANIZATION = "organization"
    ARTICLE = "article"


class RelationshipType(str, enum.Enum):
    RELATED_TO = "related_to"
    SUSPECTED = "suspected"
    VICTIM_OF = "victim_of"
    LOCATED_AT = "located_at"
    MEMBER_OF = "member_of"
    SIMILAR_TO = "similar_to"
    CITED_BY = "cited_by"


class Relationship(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "relationships"

    source_type: Mapped[EntityType] = mapped_column(Enum(EntityType), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    target_type: Mapped[EntityType] = mapped_column(Enum(EntityType), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    relationship_type: Mapped[RelationshipType] = mapped_column(
        Enum(RelationshipType), nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    description: Mapped[str | None] = mapped_column(Text)
