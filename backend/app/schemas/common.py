"""Shared schema utilities."""

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class SearchFilters(BaseModel):
    query: str | None = None
    countries: list[str] = Field(default_factory=list)
    crime_types: list[str] = Field(default_factory=list)
    horror_categories: list[str] = Field(default_factory=list)
    date_from: datetime | None = None
    date_to: datetime | None = None
    min_confidence: float | None = None
    min_credibility: float | None = None
    source_ids: list[UUID] = Field(default_factory=list)
    boolean_query: str | None = None
    fuzzy: bool = False
    semantic: bool = True
