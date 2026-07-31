"""Crawl orchestration service."""

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crawlers.base.crawler import CrawlItem
from app.crawlers.registry import get_crawler
from app.models.article import Article, ProcessingStatus
from app.models.source import Source, SourceStatus

logger = structlog.get_logger()


class CrawlService:
    async def run_source_crawl(
        self, db: AsyncSession, source_id: UUID, incremental: bool = True
    ) -> dict:
        source = await db.get(Source, source_id)
        if not source or source.status != SourceStatus.ACTIVE:
            return {"status": "skipped", "reason": "source inactive or not found"}

        config = {
            "base_url": source.base_url,
            "rate_limit": source.rate_limit,
            "respect_robots": source.respect_robots,
            **source.config,
        }
        if source.use_proxy and config.get("proxy_url"):
            config["proxy_url"] = config["proxy_url"]

        crawler = get_crawler(source.source_type, config)
        source.last_crawled_at = datetime.now(UTC)

        try:
            result = await crawler.crawl(incremental=incremental)
            new_count = 0
            for item in result.items:
                created = await self._store_item(db, source, item)
                if created:
                    new_count += 1

            source.last_success_at = datetime.now(UTC)
            source.last_error = None
            source.articles_count += new_count
            await db.commit()

            return {
                "status": "success",
                "source": source.slug,
                "new_articles": new_count,
                "pages_crawled": result.pages_crawled,
                "errors": result.errors,
            }
        except Exception as exc:
            source.last_error = str(exc)
            source.status = SourceStatus.ERROR
            await db.commit()
            logger.error("crawl_failed", source=source.slug, error=str(exc))
            return {"status": "error", "error": str(exc)}

    async def _store_item(self, db: AsyncSession, source: Source, item: CrawlItem) -> bool:
        existing = await db.execute(select(Article).where(Article.url == item.url))
        if existing.scalar_one_or_none():
            return False

        article = Article(
            source_id=source.id,
            url=item.url,
            title=item.title,
            content=item.content,
            author=item.author,
            published_at=item.published_at,
            external_id=item.external_id,
            fetched_at=datetime.now(UTC),
            processing_status=ProcessingStatus.PENDING,
            word_count=len(item.content.split()),
            ai_metadata=item.metadata,
        )
        db.add(article)
        return True

    async def get_crawler_status(self, db: AsyncSession) -> list[dict]:
        sources = (await db.execute(select(Source))).scalars().all()
        return [
            {
                "id": str(s.id),
                "name": s.name,
                "slug": s.slug,
                "type": s.source_type.value,
                "status": s.status.value,
                "last_crawled_at": s.last_crawled_at.isoformat() if s.last_crawled_at else None,
                "last_success_at": s.last_success_at.isoformat() if s.last_success_at else None,
                "articles_count": s.articles_count,
                "last_error": s.last_error,
            }
            for s in sources
        ]
