import functools
import logging

from langchain_community.tools.tavily_search import TavilySearchResults

from config.settings import settings

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def get_search_tool() -> TavilySearchResults:
    """Return a cached TavilySearchResults tool instance."""
    logger.info("Initializing Tavily search tool, max_results=%d", settings.SEARCH_RESULTS_PER_CLAIM)
    return TavilySearchResults(
        max_results=settings.SEARCH_RESULTS_PER_CLAIM,
        api_key=settings.TAVILY_API_KEY,
    )


def safe_search(query: str) -> list[dict]:
    """Execute a Tavily web search, returning empty list on any failure."""
    try:
        tool = get_search_tool()
        results = tool.invoke(query)
        if isinstance(results, list):
            return results
        return []
    except Exception as exc:
        logger.warning("Tavily search failed for query '%s': %s", query, exc)
        return []
