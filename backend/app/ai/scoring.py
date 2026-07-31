"""Scoring: credibility, sentiment, story potential."""

import re


def score_sentiment(text: str) -> float:
    """Simple lexicon-based sentiment (-1 to 1)."""
    negative = {"horror", "death", "murder", "fear", "terror", "gruesome", "tragic", "victim"}
    positive = {"solved", "justice", "found", "safe", "recovered", "cleared"}
    lower = text.lower()
    neg = sum(lower.count(w) for w in negative)
    pos = sum(lower.count(w) for w in positive)
    total = neg + pos + 1
    return round((pos - neg) / total, 3)


def score_credibility(text: str, source_score: float = 0.5) -> float:
    """Heuristic credibility based on source score and text signals."""
    signals = 0.0
    if re.search(r"\b(according to|officials said|police stated|court records)\b", text, re.I):
        signals += 0.15
    if re.search(r"\b( allegedly | reportedly | unnamed source )\b", text, re.I):
        signals -= 0.1
    word_count = len(text.split())
    if word_count > 500:
        signals += 0.1
    if word_count < 100:
        signals -= 0.1
    return round(min(1.0, max(0.0, source_score * 0.6 + 0.4 + signals)), 3)


def score_story_potential(text: str, entities: dict) -> float:
    """Score how compelling a case is for storytelling."""
    score = 0.3
    if entities.get("timeline"):
        score += min(0.2, len(entities["timeline"]) * 0.02)
    if entities.get("persons"):
        score += min(0.15, len(entities["persons"]) * 0.03)
    if entities.get("locations"):
        score += 0.1
    mystery_markers = ["unsolved", "mystery", "unknown", "bizarre", "strange", "unexplained"]
    lower = text.lower()
    score += min(0.25, sum(0.05 for m in mystery_markers if m in lower))
    return round(min(1.0, score), 3)
