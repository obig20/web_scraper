"""Search endpoints."""

from uuid import UUID

from fastapi import APIRouter

from app.api.deps import DbSession
from app.ai.embeddings import EmbeddingService
from app.models.article import Article
from app.schemas.search import SearchQuery, SearchResult
from app.search.service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("", response_model=SearchResult)
async def search(query: SearchQuery, db: DbSession):
    service = SearchService()
    return await service.search(query, db)


@router.get("/similar/{article_id}")
async def similar_cases(article_id: UUID, db: DbSession, limit: int = 10):
    service = SearchService()
    embeddings = EmbeddingService()
    article = await db.get(Article, article_id)
    if not article:
        return {"hits": []}
    text = f"{article.title}\n{article.summary or ''}"
    vector = await embeddings.embed(text)
    hits = await service.find_similar(str(article_id), vector, limit)
    return {"hits": hits}
