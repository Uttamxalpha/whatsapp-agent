import csv
import logging
import os

from services.chroma_service import get_chroma_client
from rag.embedder import MiniLMEmbeddingFunction
from config.settings import settings

logger = logging.getLogger(__name__)

CORPUS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fact_check_corpus.csv")


def load_corpus() -> int:
    """Load fact-check corpus CSV into ChromaDB; returns the number of documents loaded."""
    try:
        client = get_chroma_client()
        embedding_fn = MiniLMEmbeddingFunction()
        collection = client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=embedding_fn,
        )

        if not os.path.exists(CORPUS_PATH):
            logger.warning("Corpus file not found at %s", CORPUS_PATH)
            return 0

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ids.append(row["id"])
                documents.append(row["claim"])
                metadatas.append({
                    "verdict": row.get("verdict", ""),
                    "explanation": row.get("explanation", ""),
                    "source_url": row.get("source_url", ""),
                })

        if not ids:
            logger.warning("Corpus CSV is empty")
            return 0

        batch_size = 100
        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            collection.upsert(
                ids=ids[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
            )

        total = collection.count()
        logger.info("Corpus loaded: %d documents in collection '%s'", total, settings.CHROMA_COLLECTION_NAME)
        return total

    except Exception as exc:
        logger.error("Failed to load corpus: %s", exc)
        return 0
