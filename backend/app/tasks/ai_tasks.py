"""Celery AI processing tasks."""

import asyncio

import structlog
from sqlalchemy import select

from app.ai.pipeline import AIPipeline
from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.article import Article
from app.models.script import ResearchNote
from app.services.article_service import ArticleService

logger = structlog.get_logger()


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.ai_tasks.process_pending_articles")
def process_pending_articles():
    return _run_async(_process())


@celery_app.task(name="app.tasks.ai_tasks.detect_duplicates_batch")
def detect_duplicates_batch():
    return _run_async(_detect_duplicates())


@celery_app.task(name="app.tasks.ai_tasks.generate_research_note")
def generate_research_note(article_id: str):
    return _run_async(_generate_note(article_id))


async def _process() -> dict:
    service = ArticleService()
    async with AsyncSessionLocal() as db:
        count = await service.process_pending(db)
    return {"processed": count}


async def _detect_duplicates() -> dict:
    pipeline = AIPipeline()
    duplicates = 0
    async with AsyncSessionLocal() as db:
        articles = (
            await db.execute(
                select(Article).where(Article.is_duplicate.is_(False), Article.simhash.isnot(None))
            )
        ).scalars().all()
        seen_hashes: list[str] = []
        for article in articles:
            if article.simhash and pipeline.check_duplicate(article.simhash, seen_hashes):
                article.is_duplicate = True
                duplicates += 1
            elif article.simhash:
                seen_hashes.append(article.simhash)
        await db.commit()
    return {"duplicates_found": duplicates}


async def _generate_note(article_id: str) -> dict:
    from uuid import UUID

    pipeline = AIPipeline()
    async with AsyncSessionLocal() as db:
        article = await db.get(Article, UUID(article_id))
        if not article:
            return {"error": "not found"}

        notes = await pipeline.generate_notes(
            article.title,
            article.content,
            [{"url": article.url, "title": article.title}],
        )
        note = ResearchNote(
            article_id=article.id,
            case_id=article.case_id,
            title=notes["title"],
            timeline=notes.get("timeline", []),
            people_involved=notes.get("people_involved", []),
            important_facts=notes.get("important_facts", []),
            contradictions=notes.get("contradictions", []),
            interesting_details=notes.get("interesting_details", []),
            open_questions=notes.get("open_questions", []),
            related_cases=notes.get("related_cases", []),
            storytelling_angles=notes.get("storytelling_angles", []),
            thumbnail_ideas=notes.get("thumbnail_ideas", []),
            potential_titles=notes.get("potential_titles", []),
            source_citations=notes.get("source_citations", []),
        )
        db.add(note)
        await db.commit()
        return {"note_id": str(note.id)}
