"""Vector embeddings for semantic search."""

import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

_model = None


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer(settings.embedding_model)
        except Exception as exc:
            logger.warning("embedding_model_unavailable", error=str(exc))
            _model = False
    return _model


class EmbeddingService:
    async def embed(self, text: str) -> list[float]:
        model = _get_model()
        if not model:
            return [0.0] * 384
        vector = model.encode(text, show_progress_bar=False)
        return vector.tolist()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        model = _get_model()
        if not model:
            return [[0.0] * 384 for _ in texts]
        vectors = model.encode(texts, show_progress_bar=False)
        return [v.tolist() for v in vectors]
