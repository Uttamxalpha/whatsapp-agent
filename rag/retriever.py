import logging
from typing import Optional

from config.settings import settings
from services.chroma_service import get_collection
from rag.embedder import MiniLMEmbeddingFunction

logger = logging.getLogger(__name__)

_embedding_fn = MiniLMEmbeddingFunction()


def retrieve_similar_checks(query: str, k: Optional[int] = None) -> list[dict]:
    """Query ChromaDB for past fact-checks similar to the given query string."""
    try:
        top_k = k or settings.TOP_K_RAG
        collection = get_collection()

        query_embedding = _embedding_fn([query])
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        similar_checks: list[dict] = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i] if results.get("distances") else 1.0
                if distance > 0.7:
                    continue
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                similar_checks.append({
                    "claim": doc,
                    "verdict": metadata.get("verdict", ""),
                    "explanation": metadata.get("explanation", ""),
                    "source_url": metadata.get("source_url", ""),
                    "distance": distance,
                })

        logger.info("Retrieved %d similar checks for query (top_k=%d)", len(similar_checks), top_k)
        return similar_checks
    except Exception as exc:
        logger.error("RAG retrieval failed: %s", exc)
        return []
