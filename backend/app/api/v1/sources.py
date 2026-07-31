"""Source management endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import DbSession, require_permission
from app.models.source import Source
from app.schemas.common import PaginatedResponse
from app.schemas.source import SourceCreate, SourceRead, SourceUpdate
from app.tasks.crawl_tasks import crawl_source

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("", response_model=PaginatedResponse[SourceRead])
async def list_sources(db: DbSession, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    total = (await db.execute(select(Source))).scalars().all()
    items = total[offset : offset + page_size]
    return PaginatedResponse(
        items=items,
        total=len(total),
        page=page,
        page_size=page_size,
        pages=max(1, (len(total) + page_size - 1) // page_size),
    )


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
async def create_source(
    data: SourceCreate,
    db: DbSession,
    _user=require_permission("trigger:crawl"),
):
    source = Source(
        name=data.name,
        slug=data.slug,
        source_type=data.source_type,
        base_url=str(data.base_url),
        description=data.description,
        config=data.config,
        credibility_base_score=data.credibility_base_score,
        rate_limit=data.rate_limit,
        crawl_schedule=data.crawl_schedule,
    )
    db.add(source)
    await db.flush()
    return source


@router.get("/{source_id}", response_model=SourceRead)
async def get_source(source_id: UUID, db: DbSession):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.patch("/{source_id}", response_model=SourceRead)
async def update_source(
    source_id: UUID,
    data: SourceUpdate,
    db: DbSession,
    _user=require_permission("trigger:crawl"),
):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(source, field, value)
    await db.flush()
    return source


@router.post("/{source_id}/crawl")
async def trigger_crawl(
    source_id: UUID,
    incremental: bool = True,
    _user=require_permission("trigger:crawl"),
):
    task = crawl_source.delay(str(source_id), incremental)
    return {"task_id": task.id, "status": "queued"}
