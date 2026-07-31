"""Article endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleRead, ArticleSummary
from app.schemas.common import PaginatedResponse
from app.services.article_service import ArticleService
from app.tasks.ai_tasks import generate_research_note

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("", response_model=PaginatedResponse[ArticleSummary])
async def list_articles(db: DbSession, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    all_articles = (
        await db.execute(
            select(Article).where(Article.is_duplicate.is_(False)).order_by(Article.created_at.desc())
        )
    ).scalars().all()
    items = all_articles[offset : offset + page_size]
    return PaginatedResponse(
        items=items,
        total=len(all_articles),
        page=page,
        page_size=page_size,
        pages=max(1, (len(all_articles) + page_size - 1) // page_size),
    )


@router.get("/{article_id}", response_model=ArticleRead)
async def get_article(article_id: UUID, db: DbSession):
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("", response_model=ArticleRead, status_code=201)
async def create_article(data: ArticleCreate, db: DbSession):
    service = ArticleService()
    try:
        article = await service.create_article(db, data)
        await db.flush()
        return article
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{article_id}/research-notes")
async def create_research_notes(article_id: UUID):
    task = generate_research_note.delay(str(article_id))
    return {"task_id": task.id, "status": "queued"}
