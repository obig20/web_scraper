"""Analytics and dashboard metrics."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ProcessingStatus
from app.models.case import Case
from app.models.source import Source


class AnalyticsService:
    async def dashboard_stats(self, db: AsyncSession) -> dict:
        total_articles = (await db.execute(select(func.count(Article.id)))).scalar() or 0
        total_cases = (await db.execute(select(func.count(Case.id)))).scalar() or 0
        total_sources = (await db.execute(select(func.count(Source.id)))).scalar() or 0
        pending = (
            await db.execute(
                select(func.count(Article.id)).where(
                    Article.processing_status == ProcessingStatus.PENDING
                )
            )
        ).scalar() or 0

        week_ago = datetime.now(UTC) - timedelta(days=7)
        new_this_week = (
            await db.execute(
                select(func.count(Article.id)).where(Article.created_at >= week_ago)
            )
        ).scalar() or 0

        return {
            "total_articles": total_articles,
            "total_cases": total_cases,
            "total_sources": total_sources,
            "pending_processing": pending,
            "new_this_week": new_this_week,
        }

    async def trending_topics(self, db: AsyncSession, limit: int = 10) -> list[dict]:
        week_ago = datetime.now(UTC) - timedelta(days=7)
        articles = (
            await db.execute(
                select(Article.crime_types, Article.horror_categories)
                .where(Article.created_at >= week_ago)
                .limit(500)
            )
        ).all()

        freq: dict[str, int] = {}
        for crime_types, horror_cats in articles:
            for tag in (crime_types or []) + (horror_cats or []):
                freq[tag] = freq.get(tag, 0) + 1

        return [{"topic": k, "count": v} for k, v in sorted(freq.items(), key=lambda x: -x[1])[:limit]]

    async def discoveries(self, db: AsyncSession, limit: int = 20) -> list[dict]:
        articles = (
            await db.execute(
                select(Article)
                .where(Article.is_duplicate.is_(False))
                .order_by(Article.created_at.desc())
                .limit(limit)
            )
        ).scalars().all()

        return [
            {
                "id": str(a.id),
                "title": a.title,
                "crime_types": a.crime_types,
                "horror_categories": a.horror_categories,
                "story_potential_score": a.story_potential_score,
                "created_at": a.created_at.isoformat(),
            }
            for a in articles
        ]
