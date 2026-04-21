import json
import logging

from langchain_core.messages import SystemMessage, HumanMessage

from core.state import AgentState
from core.exceptions import LLMError
from services.llm_service import get_llm_json

logger = logging.getLogger(__name__)


async def verdict_node(state: AgentState) -> dict:
    """Aggregate individual claim verdicts into a final overall verdict."""
    if state.get("verdict"):
        logger.info("Verdict already set, skipping verdict node")
        return {}

    try:
        claim_results: list[dict] = state.get("claim_results", [])
        detected_language = state.get("detected_language", "en")

        formatted_results = "\n".join(
            f"- Claim: {cr.get('claim', '')} | Verdict: {cr.get('sub_verdict', '')} | "
            f"Confidence: {cr.get('confidence', 0.0)} | Evidence: {cr.get('evidence_summary', '')}"
            for cr in claim_results
        )

        system_prompt = (
            "You are a senior misinformation analyst. Determine the overall verdict.\n\n"
            f"Individual claim verdicts:\n{formatted_results}\n\n"
            f"Original message language: {detected_language}\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            '  "verdict": "TRUE" | "FALSE" | "MISLEADING" | "UNVERIFIABLE",\n'
            '  "confidence": 0.0-1.0,\n'
            '  "explanation": "2-3 sentences in the SAME language as the original message"\n'
            "}\n\n"
            "Verdict logic:\n"
            "- If ANY major claim is FALSE -> overall FALSE\n"
            "- If claims are partially true or context is distorted -> MISLEADING\n"
            "- Only TRUE if ALL claims are verified true\n"
            "- UNVERIFIABLE if evidence is insufficient"
        )

        llm = get_llm_json()
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content="Determine the overall verdict based on the individual claim analyses above."),
        ])

        parsed = json.loads(response.content)

        all_sources: list[str] = []
        for cr in claim_results:
            for src in cr.get("sources", []):
                if src and src not in all_sources:
                    all_sources.append(src)

        logger.info("Verdict node: verdict=%s, confidence=%s", parsed.get("verdict"), parsed.get("confidence"))
        return {
            "verdict": parsed.get("verdict", "UNVERIFIABLE"),
            "confidence": float(parsed.get("confidence", 0.0)),
            "explanation": parsed.get("explanation", ""),
            "sources": all_sources,
        }

    except json.JSONDecodeError as exc:
        logger.error("Failed to parse verdict JSON: %s", exc)
        raise LLMError(f"Verdict JSON parse failed: {exc}") from exc
    except Exception as exc:
        logger.error("Verdict node failed: %s", exc)
        raise LLMError(f"Verdict generation failed: {exc}") from exc
