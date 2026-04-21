import functools
import logging
from typing import List

from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from sentence_transformers import SentenceTransformer

from config.settings import settings

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Return a cached SentenceTransformer model instance."""
    logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
    return SentenceTransformer(settings.EMBEDDING_MODEL)


class MiniLMEmbeddingFunction(EmbeddingFunction):
    """ChromaDB-compatible embedding function using sentence-transformers."""

    def __call__(self, input: Documents) -> Embeddings:
        """Encode input documents and return embeddings as list of lists."""
        model = get_embedding_model()
        embeddings = model.encode(list(input), show_progress_bar=False)
        return embeddings.tolist()
