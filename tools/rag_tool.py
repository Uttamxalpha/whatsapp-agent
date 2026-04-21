import functools
import logging

from langchain.tools import Tool

from rag.retriever import retrieve_similar_checks

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def get_rag_tool() -> Tool:
    """Return a cached LangChain Tool wrapping the RAG retriever."""
    logger.info("Initializing RAG tool")
    return Tool(
        name="past_fact_checks",
        description="Search previously verified Indian misinformation fact-checks. Always call this before web search.",
        func=lambda query: retrieve_similar_checks(query),
    )
