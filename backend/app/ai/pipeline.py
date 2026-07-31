"""AI processing pipeline orchestrator."""

from dataclasses import dataclass, field

import structlog

from app.ai.classifiers import classify_crime_types, classify_horror_categories
from app.ai.deduplication import compute_content_hash, compute_simhash, find_similar_hashes
from app.ai.embeddings import EmbeddingService
from app.ai.extraction import EntityExtractor
from app.ai.scoring import score_credibility, score_sentiment, score_story_potential
from app.ai.summarization import summarize_text
from app.ai.writing_assistant import generate_research_notes

logger = structlog.get_logger()


@dataclass
class PipelineResult:
    summary: str = ""
    entities: dict = field(default_factory=dict)
    crime_types: list[str] = field(default_factory=list)
    horror_categories: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    sentiment_score: float = 0.0
    credibility_score: float = 0.5
    story_potential_score: float = 0.5
    confidence_score: float = 0.5
    content_hash: str = ""
    simhash: str = ""
    embedding: list[float] = field(default_factory=list)
    timeline: list[dict] = field(default_factory=list)
    people: list[dict] = field(default_factory=list)
    locations: list[dict] = field(default_factory=list)


class AIPipeline:
    """Runs the full NLP/ML pipeline on article content."""

    def __init__(self) -> None:
        self.extractor = EntityExtractor()
        self.embeddings = EmbeddingService()

    async def process(
        self,
        title: str,
        content: str,
        source_credibility: float = 0.5,
    ) -> PipelineResult:
        logger.info("ai_pipeline_start", title=title[:80])
        text = f"{title}\n\n{content}"

        entities = self.extractor.extract_all(text)
        summary = summarize_text(text)
        crime_types = classify_crime_types(text)
        horror_categories = classify_horror_categories(text)
        sentiment = score_sentiment(text)
        credibility = score_credibility(text, source_credibility)
        story_potential = score_story_potential(text, entities)
        keywords = self.extractor.extract_keywords(text)
        embedding = await self.embeddings.embed(text[:8000])
        content_hash = compute_content_hash(content)
        simhash_val = compute_simhash(content)

        confidence = min(1.0, credibility * 0.4 + (len(entities.get("persons", [])) > 0) * 0.2 + 0.4)

        return PipelineResult(
            summary=summary,
            entities=entities,
            crime_types=crime_types,
            horror_categories=horror_categories,
            keywords=keywords,
            sentiment_score=sentiment,
            credibility_score=credibility,
            story_potential_score=story_potential,
            confidence_score=confidence,
            content_hash=content_hash,
            simhash=simhash_val,
            embedding=embedding,
            timeline=entities.get("timeline", []),
            people=entities.get("persons", []),
            locations=entities.get("locations", []),
        )

    async def generate_notes(
        self,
        title: str,
        content: str,
        sources: list[dict],
        related_cases: list[dict] | None = None,
    ) -> dict:
        return await generate_research_notes(title, content, sources, related_cases or [])

    def check_duplicate(self, simhash: str, existing_simhashes: list[str]) -> str | None:
        return find_similar_hashes(simhash, existing_simhashes)
