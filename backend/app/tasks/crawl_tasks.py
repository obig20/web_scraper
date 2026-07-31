"""Celery crawl tasks."""

import asyncio

import structlog
from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.source import Source, SourceStatus
from app.services.crawl_service import CrawlService

logger = structlog.get_logger()


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.crawl_tasks.run_scheduled_crawls", bind=True, max_retries=3)
def run_scheduled_crawls(self):
    return _run_async(_run_all_crawls(incremental=False))


@celery_app.task(name="app.tasks.crawl_tasks.run_incremental_crawls", bind=True, max_retries=3)
def run_incremental_crawls(self):
    return _run_async(_run_all_crawls(incremental=True))


@celery_app.task(name="app.tasks.crawl_tasks.crawl_source", bind=True, max_retries=5)
def crawl_source(self, source_id: str, incremental: bool = True):
    return _run_async(_crawl_single(source_id, incremental))


async def _run_all_crawls(incremental: bool) -> dict:
    service = CrawlService()
    results = []
    async with AsyncSessionLocal() as db:
        sources = (
            await db.execute(select(Source).where(Source.status == SourceStatus.ACTIVE))
        ).scalars().all()
        for source in sources:
            result = await service.run_source_crawl(db, source.id, incremental=incremental)
            results.append(result)
    return {"crawled": len(results), "results": results}


async def _crawl_single(source_id: str, incremental: bool) -> dict:
    from uuid import UUID

    service = CrawlService()
    async with AsyncSessionLocal() as db:
        return await service.run_source_crawl(db, UUID(source_id), incremental=incremental)
