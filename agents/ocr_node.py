import logging
import re

import httpx

from core.state import AgentState
from services.ocr_service import extract_text_from_base64

logger = logging.getLogger(__name__)


def _detect_language(text: str) -> str:
    """Detect whether text is English, Hindi, or mixed based on Unicode ranges."""
    if not text:
        return "en"
    hindi_chars = len(re.findall(r"[\u0900-\u097F]", text))
    total_alpha = len(re.findall(r"[a-zA-Z\u0900-\u097F]", text))
    if total_alpha == 0:
        return "en"
    hindi_ratio = hindi_chars / total_alpha
    if hindi_ratio > 0.5:
        return "hi"
    elif hindi_ratio > 0.2:
        return "mixed"
    return "en"


async def ocr_node(state: AgentState) -> dict:
    """Extract text from the raw input based on input_type (image/text/url)."""
    try:
        input_type = state.get("input_type", "text")
        raw_input = state.get("raw_input", "")

        if input_type == "image":
            extracted_text = extract_text_from_base64(raw_input)
        elif input_type == "url":
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(raw_input)
                response.raise_for_status()
                html_content = response.text
                extracted_text = re.sub(r"<[^>]+>", " ", html_content)
                extracted_text = re.sub(r"\s+", " ", extracted_text).strip()
        else:
            extracted_text = raw_input

        detected_language = _detect_language(extracted_text)
        logger.info("OCR node: type=%s, lang=%s, text_len=%d", input_type, detected_language, len(extracted_text))
        return {"extracted_text": extracted_text, "detected_language": detected_language}

    except Exception as exc:
        logger.error("OCR node failed: %s", exc)
        return {"error": str(exc), "extracted_text": "", "detected_language": "en"}
