"""Research note and script schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.models.script import ScriptStatus
from app.schemas.common import ORMBase


class ScriptCreate(BaseModel):
    case_id: UUID | None = None
    title: str = Field(min_length=1, max_length=512)
    content: str = Field(min_length=1)
    source_article_ids: list[str] = Field(default_factory=list)


class ScriptRead(ORMBase):
    id: UUID
    case_id: UUID | None
    title: str
    content: str
    status: ScriptStatus
    version: int
    source_article_ids: list[str]


class ResearchNoteRead(ORMBase):
    id: UUID
    case_id: UUID | None
    article_id: UUID | None
    title: str
    timeline: list
    people_involved: list
    important_facts: list
    contradictions: list
    interesting_details: list
    open_questions: list
    related_cases: list
    storytelling_angles: list
    thumbnail_ideas: list
    potential_titles: list
    source_citations: list
