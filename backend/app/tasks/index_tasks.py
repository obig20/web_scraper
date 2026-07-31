"""Elasticsearch indexing tasks."""

import asyncio
from datetime import UTC, datetime

import structlog
from sqlalchemy import select

from app.ai.embeddings import EmbeddingService
from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.article import Article
from app.search.service import SearchService

logger = structlog.get_logger()


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.index_tasks.incremental_reindex")
def incremental_reindex():
    return _run_async(_reindex())


@celery_app.task(name="app.tasks.index_tasks.index_article")
def index_article(article_id: str):
    return _run_async(_index_single(article_id))


async def _reindex() -> dict:
    search = SearchService()
    embeddings = EmbeddingService()
    await search.ensure_index()
    indexed = 0

    async with AsyncSessionLocal() as db:
        articles = (
            await db.execute(
                select(Article).where(
                    Article.indexed_at.is_(None),
                    Article.is_duplicate.is_(False),
                ).limit(100)
            )
        ).scalars().all()

        for article in articles:
            text = f"{article.title}\n{article.summary or article.content[:2000]}"
            embedding = await embeddings.embed(text)
            await search.index_article(article, embedding)
            article.indexed_at = datetime.now(UTC)
            indexed += 1

        await db.commit()

    return {"indexed": indexed}


async def _index_single(article_id: str) -> dict:
    from uuid import UUID

    search = SearchService()
    embeddings = EmbeddingService()
    async with AsyncSessionLocal() as db:
        article = await db.get(Article, UUID(article_id))
        if not article:
            return {"error": "not found"}
        text = f"{article.title}\n{article.summary or article.content[:2000]}"
        embedding = await embeddings.embed(text)
        await search.index_article(article, embedding)
        article.indexed_at = datetime.now(UTC)
        await db.commit()
    return {"status": "indexed"}
