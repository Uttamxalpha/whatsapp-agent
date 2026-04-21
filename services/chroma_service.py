import functools
import logging

import chromadb

from config.settings import settings
from core.exceptions import ChromaError

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.ClientAPI:
    """Return a cached persistent ChromaDB client."""
    try:
        logger.info("Initializing ChromaDB client at %s", settings.CHROMA_PERSIST_DIR)
        return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    except Exception as exc:
        logger.error("Failed to initialize ChromaDB client: %s", exc)
        raise ChromaError(f"ChromaDB client init failed: {exc}") from exc


@functools.lru_cache(maxsize=1)
def get_collection() -> chromadb.Collection:
    """Return or create the fact-checks ChromaDB collection."""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(name=settings.CHROMA_COLLECTION_NAME)
        logger.info("ChromaDB collection '%s' ready, count=%d", settings.CHROMA_COLLECTION_NAME, collection.count())
        return collection
    except Exception as exc:
        logger.error("Failed to get/create ChromaDB collection: %s", exc)
        raise ChromaError(f"ChromaDB collection error: {exc}") from exc
