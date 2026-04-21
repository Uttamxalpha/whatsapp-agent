import json
import logging

from langchain_core.messages import SystemMessage, HumanMessage

from core.state import AgentState
from core.exceptions import LLMError
from services.llm_service import get_llm_json
from config.settings import settings

logger = logging.getLogger(__name__)


async def claim_extractor_node(state: AgentState) -> dict:
    """Extract verifiable factual claims from the extracted text using LLM."""
    try:
        extracted_text = state.get("extracted_text", "")

        if not extracted_text.strip():
            logger.warning("Claim extractor received empty text")
            return {
                "claims": [],
                "verdict": "UNVERIFIABLE",
                "confidence": 0.0,
                "explanation": "No text found to analyze.",
                "sources": [],
                "claim_results": [],
            }

        system_prompt = (
            "You are a claim extraction specialist for Indian misinformation detection. "
            "Extract only specific, verifiable factual claims from the given WhatsApp message. "
            "Ignore opinions, emotions, religious sentiments, and calls to action. "
            'Return ONLY a JSON object: {"claims": ["claim 1", "claim 2"]} '
            f"Maximum {settings.MAX_CLAIMS} claims. Keep claims in their original language. "
            'If no verifiable claims exist, return {"claims": []}.'
        )

        llm = get_llm_json()
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=extracted_text),
        ])

        parsed = json.loads(response.content)
        claims: list[str] = parsed.get("claims", [])

        if not claims:
            logger.info("No verifiable claims found in text")
            return {
                "claims": [],
                "verdict": "UNVERIFIABLE",
                "confidence": 0.0,
                "explanation": "No verifiable factual claims found in this message.",
                "sources": [],
                "claim_results": [],
            }

        logger.info("Extracted %d claims", len(claims))
        return {"claims": claims}

    except json.JSONDecodeError as exc:
        logger.error("Failed to parse LLM JSON response: %s", exc)
        raise LLMError(f"Claim extraction JSON parse failed: {exc}") from exc
    except Exception as exc:
        logger.error("Claim extractor failed: %s", exc)
        raise LLMError(f"Claim extraction failed: {exc}") from exc
