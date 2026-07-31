"""Duplicate detection via content hash and simhash."""

import hashlib
import re

from simhash import Simhash


def compute_content_hash(content: str) -> str:
    normalized = re.sub(r"\s+", " ", content.lower().strip())
    return hashlib.sha256(normalized.encode()).hexdigest()


def compute_simhash(content: str) -> str:
    tokens = re.findall(r"\b\w+\b", content.lower())
    return str(Simhash(tokens).value)


def find_similar_hashes(simhash_str: str, existing: list[str], threshold: int = 3) -> str | None:
    """Return matching simhash if Hamming distance <= threshold."""
    if not simhash_str or not existing:
        return None
    target = Simhash(int(simhash_str))
    for existing_hash in existing:
        try:
            other = Simhash(int(existing_hash))
            if target.distance(other) <= threshold:
                return existing_hash
        except (ValueError, TypeError):
            continue
    return None
