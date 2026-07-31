"""Unified search service: full-text, semantic, boolean, fuzzy."""

import time
from typing import Any

import structlog
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import EmbeddingService
from app.config import get_settings
from app.core.elasticsearch import INDEX_MAPPING, get_es_client
from app.models.article import Article
from app.schemas.search import SearchHit, SearchQuery, SearchResult

logger = structlog.get_logger()
settings = get_settings()


class SearchService:
    def __init__(self) -> None:
        self.embeddings = EmbeddingService()

    async def ensure_index(self) -> None:
        es = await get_es_client()
        if not await es.indices.exists(index=settings.elasticsearch_index):
            await es.indices.create(index=settings.elasticsearch_index, body=INDEX_MAPPING)

    async def search(self, query: SearchQuery, db: AsyncSession) -> SearchResult:
        start = time.perf_counter()
        es_hits: list[SearchHit] = []
        total = 0

        try:
            es = await get_es_client()
            body = await self._build_es_query(query)
            response = await es.search(
                index=settings.elasticsearch_index,
                body=body,
                from_=(query.page - 1) * query.page_size,
                size=query.page_size,
            )
            total = response["hits"]["total"]["value"]
            for hit in response["hits"]["hits"]:
                src = hit["_source"]
                es_hits.append(
                    SearchHit(
                        id=hit["_id"],
                        article_id=src.get("article_id"),
                        case_id=src.get("case_id"),
                        title=src.get("title", ""),
                        summary=src.get("summary"),
                        score=hit["_score"],
                        crime_types=src.get("crime_types", []),
                        horror_categories=src.get("horror_categories", []),
                        country=src.get("country"),
                        published_at=src.get("published_at"),
                        highlight=hit.get("highlight"),
                    )
                )
        except Exception as exc:
            logger.warning("es_search_fallback", error=str(exc))
            es_hits, total = await self._postgres_fallback(query, db)

        took = (time.perf_counter() - start) * 1000
        return SearchResult(
            hits=es_hits,
            total=total,
            page=query.page,
            page_size=query.page_size,
            took_ms=round(took, 2),
        )

    async def _build_es_query(self, query: SearchQuery) -> dict[str, Any]:
        must: list[dict] = []
        should: list[dict] = []
        filter_clauses: list[dict] = []

        if query.query:
            if query.boolean_query:
                must.append({"query_string": {"query": query.boolean_query, "fields": ["title^3", "content", "summary"]}})
            elif query.fuzzy:
                must.append({
                    "multi_match": {
                        "query": query.query,
                        "fields": ["title^3", "content", "summary"],
                        "fuzziness": "AUTO",
                    }
                })
            else:
                must.append({
                    "multi_match": {
                        "query": query.query,
                        "fields": ["title^3", "content", "summary"],
                        "type": "best_fields",
                    }
                })

        if query.semantic and query.query:
            embedding = await self.embeddings.embed(query.query)
            should.append({
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": embedding},
                    },
                }
            })

        if query.countries:
            filter_clauses.append({"terms": {"country": query.countries}})
        if query.crime_types:
            filter_clauses.append({"terms": {"crime_types": query.crime_types}})
        if query.horror_categories:
            filter_clauses.append({"terms": {"horror_categories": query.horror_categories}})
        if query.date_from or query.date_to:
            date_range: dict = {}
            if query.date_from:
                date_range["gte"] = query.date_from.isoformat()
            if query.date_to:
                date_range["lte"] = query.date_to.isoformat()
            filter_clauses.append({"range": {"published_at": date_range}})
        if query.min_confidence is not None:
            filter_clauses.append({"range": {"confidence_score": {"gte": query.min_confidence}}})
        if query.min_credibility is not None:
            filter_clauses.append({"range": {"credibility_score": {"gte": query.min_credibility}}})

        bool_query: dict[str, Any] = {}
        if must:
            bool_query["must"] = must
        if should:
            bool_query["should"] = should
            bool_query["minimum_should_match"] = 0 if must else 1
        if filter_clauses:
            bool_query["filter"] = filter_clauses
        if not bool_query:
            bool_query = {"must": [{"match_all": {}}]}

        return {
            "query": {"bool": bool_query},
            "highlight": {"fields": {"title": {}, "content": {"fragment_size": 150}}},
            "sort": [{query.sort_by: {"order": query.sort_order}}],
        }

    async def _postgres_fallback(
        self, query: SearchQuery, db: AsyncSession
    ) -> tuple[list[SearchHit], int]:
        stmt = select(Article).where(Article.is_duplicate.is_(False))
        if query.query:
            pattern = f"%{query.query}%"
            stmt = stmt.where(or_(Article.title.ilike(pattern), Article.content.ilike(pattern)))
        if query.countries:
            stmt = stmt.where(Article.country.in_(query.countries))
        if query.min_confidence is not None:
            stmt = stmt.where(Article.confidence_score >= query.min_confidence)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = stmt.offset((query.page - 1) * query.page_size).limit(query.page_size)
        rows = (await db.execute(stmt)).scalars().all()

        hits = [
            SearchHit(
                id=str(a.id),
                article_id=a.id,
                case_id=a.case_id,
                title=a.title,
                summary=a.summary,
                score=1.0,
                crime_types=a.crime_types or [],
                horror_categories=a.horror_categories or [],
                country=a.country,
                published_at=a.published_at,
            )
            for a in rows
        ]
        return hits, total

    async def index_article(self, article: Article, embedding: list[float]) -> None:
        es = await get_es_client()
        doc = {
            "article_id": str(article.id),
            "case_id": str(article.case_id) if article.case_id else None,
            "title": article.title,
            "content": article.content[:50000],
            "summary": article.summary,
            "keywords": article.keywords,
            "crime_types": article.crime_types,
            "horror_categories": article.horror_categories,
            "country": article.country,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "credibility_score": article.credibility_score,
            "story_potential_score": article.story_potential_score,
            "confidence_score": article.confidence_score,
            "embedding": embedding,
        }
        await es.index(index=settings.elasticsearch_index, id=str(article.id), document=doc)

    async def find_similar(self, article_id: str, embedding: list[float], limit: int = 10) -> list[dict]:
        es = await get_es_client()
        body = {
            "knn": {
                "field": "embedding",
                "query_vector": embedding,
                "k": limit,
                "num_candidates": limit * 10,
            },
            "query": {"bool": {"must_not": [{"term": {"article_id": article_id}}]}},
        }
        response = await es.search(index=settings.elasticsearch_index, body=body, size=limit)
        return [{"id": h["_id"], "score": h["_score"], **h["_source"]} for h in response["hits"]["hits"]]
