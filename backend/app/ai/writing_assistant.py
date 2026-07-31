"""AI writing assistant for research notes."""

from app.ai.summarization import summarize_text
from app.config import get_settings

settings = get_settings()


async def generate_research_notes(
    title: str,
    content: str,
    sources: list[dict],
    related_cases: list[dict],
) -> dict:
    """Generate structured research notes with factual citations.

    Uses OpenAI when configured; otherwise falls back to extractive pipeline.
    """
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return await _generate_with_openai(title, content, sources, related_cases)
    return _generate_local(title, content, sources, related_cases)


def _generate_local(
    title: str,
    content: str,
    sources: list[dict],
    related_cases: list[dict],
) -> dict:
    from app.ai.extraction import EntityExtractor
    from app.ai.classifiers import classify_crime_types, classify_horror_categories

    extractor = EntityExtractor()
    entities = extractor.extract_all(content)
    summary = summarize_text(content)

    citations = [
        {"url": s.get("url", ""), "title": s.get("title", ""), "publisher": s.get("publisher", "")}
        for s in sources
    ]

    return {
        "title": f"Research Notes: {title}",
        "timeline": entities.get("timeline", [])[:10],
        "people_involved": entities.get("persons", [])[:15],
        "important_facts": [summary],
        "contradictions": [],
        "interesting_details": _extract_interesting(content),
        "open_questions": _generate_questions(content, classify_crime_types(content)),
        "related_cases": related_cases[:5],
        "storytelling_angles": _story_angles(content, classify_horror_categories(content)),
        "thumbnail_ideas": _thumbnail_ideas(title),
        "potential_titles": _potential_titles(title),
        "source_citations": citations,
    }


async def _generate_with_openai(
    title: str,
    content: str,
    sources: list[dict],
    related_cases: list[dict],
) -> dict:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    source_list = "\n".join(f"- {s.get('title', '')}: {s.get('url', '')}" for s in sources)

    prompt = f"""Analyze this public research material and produce structured research notes.
IMPORTANT: Only state facts from the source. Do not copy text verbatim. Cite sources.
Do not invent facts.

Title: {title}
Sources:
{source_list}

Content excerpt:
{content[:6000]}

Return JSON with keys: timeline, people_involved, important_facts, contradictions,
interesting_details, open_questions, related_cases, storytelling_angles,
thumbnail_ideas, potential_titles, source_citations"""

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    import json

    result = json.loads(response.choices[0].message.content or "{}")
    result["title"] = f"Research Notes: {title}"
    return result


def _extract_interesting(text: str) -> list[str]:
    markers = ["unusual", "bizarre", "strange", "rare", "first time", "never before", "mysterious"]
    sentences = text.replace("\n", " ").split(". ")
    return [s.strip() + "." for s in sentences if any(m in s.lower() for m in markers)][:5]


def _generate_questions(text: str, crime_types: list[str]) -> list[str]:
    questions = []
    if "unsolved" in crime_types or "missing" in crime_types:
        questions.append("What happened in the final hours before the disappearance?")
    if "murder" in crime_types:
        questions.append("What forensic evidence remains unexamined?")
    questions.append("Are there conflicting witness accounts in the source material?")
    return questions[:5]


def _story_angles(text: str, horror_cats: list[str]) -> list[str]:
    angles = ["Timeline reconstruction from public records"]
    if "paranormal" in horror_cats:
        angles.append("Compare eyewitness accounts vs. official explanation")
    if "unsolved" in text.lower():
        angles.append("Explore theories while clearly labeling speculation")
    return angles


def _thumbnail_ideas(title: str) -> list[str]:
    return [
        f"Dark moody map related to: {title[:40]}",
        "Newspaper clipping collage aesthetic",
        "Silhouette figure in fog",
    ]


def _potential_titles(title: str) -> list[str]:
    base = title[:60]
    return [base, f"The Mystery of {base}", f"Unsolved: {base}", f"What Happened to {base}?"]
