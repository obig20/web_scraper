"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import articles, auth, cases, dashboard, search, sources

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(sources.router)
api_router.include_router(articles.router)
api_router.include_router(cases.router)
api_router.include_router(search.router)
api_router.include_router(dashboard.router)
