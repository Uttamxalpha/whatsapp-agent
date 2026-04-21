from typing import TypedDict, Optional


class AgentState(TypedDict):
    """LangGraph agent state definition for the misinformation checking pipeline."""

    input_type: str
    raw_input: str
    extracted_text: str
    detected_language: str
    claims: list[str]
    claim_results: list[dict]
    verdict: str
    confidence: float
    explanation: str
    sources: list[str]
    processing_time_ms: int
    error: Optional[str]
