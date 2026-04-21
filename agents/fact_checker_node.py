import json
import logging

from langchain_core.messages import SystemMessage, HumanMessage

from core.state import AgentState
from core.exceptions import LLMError
from services.llm_service import get_llm_json
from tools.search_tool import safe_search
from rag.retriever import retrieve_similar_checks

logger = logging.getLogger(__name__)


def _format_rag_results(results: list[dict]) -> str:
    """Format RAG results into a readable string for the LLM prompt."""
    if not results:
        return "No past fact-checks found."
    lines: list[str] = []
    for i, r in enumerate(results, 1):
        lines.append(
            f"{i}. Claim: {r.get('claim', '')} | Verdict: {r.get('verdict', '')} | "
            f"Explanation: {r.get('explanation', '')} | Source: {r.get('source_url', '')}"
        )
    return "\n".join(lines)


def _format_search_results(results: list[dict]) -> str:
    """Format Tavily search results into a readable string for the LLM prompt."""
    if not results:
        return "No web search results found."
    lines: list[str] = []
    for i, r in enumerate(results, 1):
        url = r.get("url", "")
        content = r.get("content", "")
        lines.append(f"{i}. {url}\n   {content[:300]}")
    return "\n".join(lines)


async def fact_checker_node(state: AgentState) -> dict:
    """Fact-check each extracted claim using web search and RAG evidence."""
    claims: list[str] = state.get("claims", [])
    claim_results: list[dict] = []

    for claim in claims:
        try:
            search_results = safe_search(claim)
            rag_results = retrieve_similar_checks(claim)

            rag_formatted = _format_rag_results(rag_results)
            search_formatted = _format_search_results(search_results)

            system_prompt = (
                "You are a professional fact-checker specializing in Indian misinformation. "
                "Analyze the claim against all provided evidence.\n\n"
                f"Claim: {claim}\n\n"
                f"Past fact-checks from database:\n{rag_formatted}\n\n"
                f"Web search results:\n{search_formatted}\n\n"
                "Return ONLY this JSON:\n"
                "{\n"
                '  "sub_verdict": "TRUE" | "FALSE" | "MISLEADING" | "UNVERIFIABLE",\n'
                '  "confidence": 0.0-1.0,\n'
                '  "evidence_summary": "1-2 sentence summary of evidence",\n'
                '  "relevant_sources": ["url1", "url2"]\n'
                "}\n\n"
                "Rules:\n"
                "- FALSE: direct contradiction found in credible sources\n"
                "- MISLEADING: partially true, out of context, or cherry-picked\n"
                "- TRUE: strongly supported by multiple credible sources\n"
                "- UNVERIFIABLE: insufficient evidence either way\n"
                "- Be strict. Prefer MISLEADING over TRUE when in doubt."
            )

            llm = get_llm_json()
            response = await llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Fact-check this claim: {claim}"),
            ])

            parsed = json.loads(response.content)
            claim_results.append({
                "claim": claim,
                "sub_verdict": parsed.get("sub_verdict", "UNVERIFIABLE"),
                "confidence": float(parsed.get("confidence", 0.0)),
                "evidence_summary": parsed.get("evidence_summary", ""),
                "sources": parsed.get("relevant_sources", []),
            })

        except json.JSONDecodeError as exc:
            logger.error("Failed to parse fact-check JSON for claim '%s': %s", claim, exc)
            claim_results.append({
                "claim": claim,
                "sub_verdict": "UNVERIFIABLE",
                "confidence": 0.0,
                "evidence_summary": "Failed to parse LLM response.",
                "sources": [],
            })
        except Exception as exc:
            logger.error("Fact-check failed for claim '%s': %s", claim, exc)
            claim_results.append({
                "claim": claim,
                "sub_verdict": "UNVERIFIABLE",
                "confidence": 0.0,
                "evidence_summary": f"Error during fact-checking: {exc}",
                "sources": [],
            })

    logger.info("Fact-checked %d claims", len(claim_results))
    return {"claim_results": claim_results}
