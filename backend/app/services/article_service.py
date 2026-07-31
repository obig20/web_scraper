"""Article ingestion and processing service."""

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.pipeline import AIPipeline
from app.models.article import Article, ProcessingStatus
from app.models.reference import Reference
from app.models.source import Source
from app.schemas.article import ArticleCreate

logger = structlog.get_logger()


class ArticleService:
    def __init__(self) -> None:
        self.pipeline = AIPipeline()

    async def create_article(self, db: AsyncSession, data: ArticleCreate) -> Article:
        existing = await db.execute(select(Article).where(Article.url == data.url))
        if existing.scalar_one_or_none():
            raise ValueError(f"Article already exists: {data.url}")

        result = await self.pipeline.process(data.title, data.content)
        article = Article(
            source_id=data.source_id,
            url=data.url,
            title=data.title,
            content=data.content,
            author=data.author,
            published_at=data.published_at,
            external_id=data.external_id,
            fetched_at=datetime.now(UTC),
            content_hash=result.content_hash,
            simhash=result.simhash,
            summary=result.summary,
            crime_types=result.crime_types,
            horror_categories=result.horror_categories,
            keywords=result.keywords,
            sentiment_score=result.sentiment_score,
            credibility_score=result.credibility_score,
            story_potential_score=result.story_potential_score,
            confidence_score=result.confidence_score,
            entities=result.entities,
            word_count=len(data.content.split()),
            processing_status=ProcessingStatus.COMPLETED,
        )
        db.add(article)
        await db.flush()

        ref = Reference(
            article_id=article.id,
            citation_text=f"{data.title}. Retrieved from {data.url}",
            url=data.url,
            access_date=datetime.now(UTC).strftime("%Y-%m-%d"),
        )
        db.add(ref)
        return article

    async def process_pending(self, db: AsyncSession, limit: int = 50) -> int:
        stmt = (
            select(Article)
            .where(Article.processing_status == ProcessingStatus.PENDING)
            .limit(limit)
        )
        articles = (await db.execute(stmt)).scalars().all()
        source_cache: dict[UUID, float] = {}

        for article in articles:
            article.processing_status = ProcessingStatus.PROCESSING
            if article.source_id not in source_cache:
                source = await db.get(Source, article.source_id)
                source_cache[article.source_id] = source.credibility_base_score if source else 0.5

            result = await self.pipeline.process(
                article.title, article.content, source_cache[article.source_id]
            )
            article.summary = result.summary
            article.crime_types = result.crime_types
            article.horror_categories = result.horror_categories
            article.keywords = result.keywords
            article.sentiment_score = result.sentiment_score
            article.credibility_score = result.credibility_score
            article.story_potential_score = result.story_potential_score
            article.confidence_score = result.confidence_score
            article.entities = result.entities
            article.content_hash = result.content_hash
            article.simhash = result.simhash
            article.processing_status = ProcessingStatus.COMPLETED

        await db.commit()
        return len(articles)
