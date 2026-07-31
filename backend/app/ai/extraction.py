"""Named entity and structured fact extraction."""

import re
from datetime import datetime

import structlog

logger = structlog.get_logger()

# Lazy-loaded spaCy model
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy

            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spacy_model_missing", hint="python -m spacy download en_core_web_sm")
            _nlp = False
    return _nlp


CRIME_KEYWORDS = {
    "murder", "homicide", "kidnapping", "robbery", "assault", "fraud",
    "disappearance", "missing", "unsolved", "cold case", "serial",
}

HORROR_KEYWORDS = {
    "paranormal", "ghost", "haunted", "ufo", "cryptid", "folklore",
    "legend", "curse", "supernatural", "occult", "demon", "poltergeist",
}

DATE_PATTERNS = [
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
]


class EntityExtractor:
    """Extracts NER entities, locations, victims, suspects, and timeline events."""

    def extract_all(self, text: str) -> dict:
        nlp = _get_nlp()
        persons, orgs, locations, gpe = [], [], [], []

        if nlp:
            doc = nlp(text[:100000])
            for ent in doc.ents:
                entry = {"text": ent.text, "label": ent.label_, "start": ent.start_char}
                if ent.label_ == "PERSON":
                    persons.append(entry)
                elif ent.label_ == "ORG":
                    orgs.append(entry)
                elif ent.label_ in ("GPE", "LOC"):
                    gpe.append(entry)
                    locations.append(entry)
                elif ent.label_ == "DATE":
                    pass  # handled by timeline

        timeline = self._extract_timeline(text)
        victims = self._extract_by_role(text, ["victim", "found dead", "body of", "killed"])
        suspects = self._extract_by_role(text, ["suspect", "arrested", "charged with", "accused"])

        return {
            "persons": persons,
            "organizations": orgs,
            "locations": locations + gpe,
            "timeline": timeline,
            "victims": victims,
            "suspects": suspects,
        }

    def extract_keywords(self, text: str, top_n: int = 20) -> list[str]:
        words = re.findall(r"\b[a-z]{4,}\b", text.lower())
        stop = {"that", "this", "with", "from", "have", "been", "were", "their", "about"}
        freq: dict[str, int] = {}
        for w in words:
            if w not in stop:
                freq[w] = freq.get(w, 0) + 1
        return sorted(freq, key=freq.get, reverse=True)[:top_n]

    def _extract_timeline(self, text: str) -> list[dict]:
        events = []
        for pattern in DATE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 200)
                context = text[start:end].strip()
                events.append({
                    "date_text": match.group(),
                    "context": context,
                    "occurred_at": self._parse_date(match.group()),
                })
        return events[:50]

    def _extract_by_role(self, text: str, markers: list[str]) -> list[dict]:
        results = []
        lower = text.lower()
        for marker in markers:
            idx = 0
            while True:
                pos = lower.find(marker, idx)
                if pos == -1:
                    break
                snippet = text[max(0, pos - 50): min(len(text), pos + 150)]
                results.append({"marker": marker, "context": snippet.strip()})
                idx = pos + len(marker)
        return results[:20]

    @staticmethod
    def _parse_date(date_str: str) -> str | None:
        for fmt in ("%B %d, %Y", "%B %d %Y", "%m/%d/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str.replace(",", ""), fmt.replace(",", "")).isoformat()
            except ValueError:
                continue
        return None
