"""Elasticsearch / OpenSearch client wrapper."""

from typing import Any

from elasticsearch import AsyncElasticsearch

from app.config import get_settings

settings = get_settings()
_es_client: AsyncElasticsearch | None = None


async def get_es_client() -> AsyncElasticsearch:
    global _es_client
    if _es_client is None:
        _es_client = AsyncElasticsearch(settings.elasticsearch_url)
    return _es_client


async def close_es_client() -> None:
    global _es_client
    if _es_client:
        await _es_client.close()
        _es_client = None


INDEX_MAPPING: dict[str, Any] = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "fuzzy_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding"],
                }
            }
        },
    },
    "mappings": {
        "properties": {
            "article_id": {"type": "keyword"},
            "case_id": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "fuzzy_analyzer"},
            "content": {"type": "text", "analyzer": "fuzzy_analyzer"},
            "summary": {"type": "text"},
            "keywords": {"type": "keyword"},
            "crime_types": {"type": "keyword"},
            "horror_categories": {"type": "keyword"},
            "country": {"type": "keyword"},
            "locations": {"type": "geo_point"},
            "published_at": {"type": "date"},
            "credibility_score": {"type": "float"},
            "story_potential_score": {"type": "float"},
            "confidence_score": {"type": "float"},
            "embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine",
            },
        }
    },
}
