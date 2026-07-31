"""Text summarization."""

import re


def summarize_text(text: str, max_sentences: int = 5) -> str:
    """Extractive summarization using sentence scoring."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if len(sentences) <= max_sentences:
        return text[:2000]

    word_freq: dict[str, int] = {}
    for word in re.findall(r"\b[a-z]{4,}\b", text.lower()):
        word_freq[word] = word_freq.get(word, 0) + 1

    scored = []
    for i, sent in enumerate(sentences):
        if len(sent) < 20:
            continue
        score = sum(word_freq.get(w, 0) for w in re.findall(r"\b[a-z]{4,}\b", sent.lower()))
        # Boost first sentences
        if i < 3:
            score *= 1.5
        scored.append((score, i, sent))

    top = sorted(scored, key=lambda x: x[0], reverse=True)[:max_sentences]
    top.sort(key=lambda x: x[1])
    return " ".join(s[2] for s in top)[:2000]
