"""Dashboard and analytics endpoints."""

from fastapi import APIRouter

from app.api.deps import DbSession
from app.services.analytics_service import AnalyticsService
from app.services.crawl_service import CrawlService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats(db: DbSession):
    service = AnalyticsService()
    return await service.dashboard_stats(db)


@router.get("/trending")
async def get_trending(db: DbSession, limit: int = 10):
    service = AnalyticsService()
    return await service.trending_topics(db, limit)


@router.get("/discoveries")
async def get_discoveries(db: DbSession, limit: int = 20):
    service = AnalyticsService()
    return await service.discoveries(db, limit)


@router.get("/crawler-status")
async def crawler_status(db: DbSession):
    service = CrawlService()
    return await service.get_crawler_status(db)
