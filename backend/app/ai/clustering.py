"""Topic clustering for case grouping."""

import structlog
import numpy as np

logger = structlog.get_logger()


def cluster_embeddings(embeddings: list[list[float]], n_clusters: int = 10) -> list[int]:
    """Cluster articles/cases by embedding vectors."""
    if len(embeddings) < 2:
        return [0] * len(embeddings)

    try:
        from sklearn.cluster import MiniBatchKMeans

        X = np.array(embeddings)
        k = min(n_clusters, len(embeddings))
        model = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=256)
        return model.fit_predict(X).tolist()
    except Exception as exc:
        logger.warning("clustering_failed", error=str(exc))
        return list(range(len(embeddings)))
