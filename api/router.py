import base64
import logging
import time

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from core.models import CheckRequest, CheckResponse, ClaimResult, HealthResponse
from core.state import AgentState
from agents.graph import compiled_graph
from services.chroma_service import get_collection
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class TextInput(BaseModel):
    """Convenience request body for plain text input."""
    text: str


def _build_initial_state(input_type: str, content: str) -> dict:
    """Build a minimal AgentState dict for graph invocation."""
    return {
        "input_type": input_type,
        "raw_input": content,
        "extracted_text": "",
        "detected_language": "",
        "claims": [],
        "claim_results": [],
        "verdict": "",
        "confidence": 0.0,
        "explanation": "",
        "sources": [],
        "processing_time_ms": 0,
        "error": None,
    }


def _build_response(result: dict, processing_time_ms: int) -> CheckResponse:
    """Convert graph output into a CheckResponse."""
    claim_results = [
        ClaimResult(
            claim=cr.get("claim", ""),
            verdict=cr.get("sub_verdict", "UNVERIFIABLE"),
            confidence=float(cr.get("confidence", 0.0)),
            evidence_summary=cr.get("evidence_summary", ""),
            sources=cr.get("sources", []),
        )
        for cr in result.get("claim_results", [])
    ]
    return CheckResponse(
        verdict=result.get("verdict", "UNVERIFIABLE"),
        confidence=float(result.get("confidence", 0.0)),
        explanation=result.get("explanation", ""),
        claim_results=claim_results,
        sources=result.get("sources", []),
        processing_time_ms=processing_time_ms,
    )


@router.post("/check", response_model=CheckResponse)
async def check(request: CheckRequest) -> CheckResponse:
    """Run the full misinformation checking pipeline on the given input."""
    if request.input_type not in ("text", "image", "url"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="input_type must be one of: text, image, url")

    initial_state = _build_initial_state(request.input_type, request.content)
    start_time = time.time()
    result = await compiled_graph.ainvoke(initial_state)
    processing_time_ms = int((time.time() - start_time) * 1000)
    logger.info("Check completed in %dms, verdict=%s", processing_time_ms, result.get("verdict"))
    return _build_response(result, processing_time_ms)


@router.post("/check/text", response_model=CheckResponse)
async def check_text(body: TextInput) -> CheckResponse:
    """Convenience endpoint for plain text fact-checking."""
    initial_state = _build_initial_state("text", body.text)
    start_time = time.time()
    result = await compiled_graph.ainvoke(initial_state)
    processing_time_ms = int((time.time() - start_time) * 1000)
    logger.info("Text check completed in %dms", processing_time_ms)
    return _build_response(result, processing_time_ms)


@router.post("/check/image", response_model=CheckResponse)
async def check_image(file: UploadFile = File(...)) -> CheckResponse:
    """Upload an image screenshot for OCR-based fact-checking."""
    contents = await file.read()
    b64_content = base64.b64encode(contents).decode("utf-8")
    initial_state = _build_initial_state("image", b64_content)
    start_time = time.time()
    result = await compiled_graph.ainvoke(initial_state)
    processing_time_ms = int((time.time() - start_time) * 1000)
    logger.info("Image check completed in %dms", processing_time_ms)
    return _build_response(result, processing_time_ms)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service health status including model info and corpus size."""
    try:
        collection = get_collection()
        corpus_size = collection.count()
    except Exception:
        corpus_size = 0
    return HealthResponse(
        status="ok",
        model=settings.GROQ_MODEL,
        corpus_size=corpus_size,
    )
