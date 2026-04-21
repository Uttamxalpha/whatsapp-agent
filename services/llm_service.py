import functools
import logging
from langchain_groq import ChatGroq
from config.settings import settings

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """Return a cached ChatGroq LLM instance."""
    logger.info("Initializing ChatGroq with model=%s", settings.GROQ_MODEL)
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=settings.GROQ_TEMPERATURE,
    )


@functools.lru_cache(maxsize=1)
def get_llm_json() -> ChatGroq:
    """Return a cached ChatGroq LLM instance bound to JSON output mode."""
    logger.info("Initializing ChatGroq (JSON mode) with model=%s", settings.GROQ_MODEL)
    llm = ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=settings.GROQ_TEMPERATURE,
    )
    return llm.bind(response_format={"type": "json_object"})
