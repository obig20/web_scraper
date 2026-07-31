"""Case schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.case import CaseStatus
from app.schemas.common import ORMBase


class CaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    slug: str = Field(min_length=1, max_length=512)
    description: str | None = None
    crime_types: list[str] = Field(default_factory=list)
    horror_categories: list[str] = Field(default_factory=list)
    country: str | None = Field(default=None, max_length=2)


class CaseSummary(ORMBase):
    id: UUID
    title: str
    slug: str
    status: CaseStatus
    crime_types: list[str]
    horror_categories: list[str]
    country: str | None
    confidence_score: float | None
    story_potential_score: float | None
    date_started: datetime | None


class CaseRead(CaseSummary):
    description: str | None
    date_ended: datetime | None
    cluster_id: int | None
