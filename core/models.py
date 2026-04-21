from pydantic import BaseModel, Field


class CheckRequest(BaseModel):
    """Request model for the fact-check endpoint."""

    input_type: str = Field(..., description="One of: text, image, url")
    content: str = Field(..., description="Raw text, base64 image, or URL string")


class ClaimResult(BaseModel):
    """Result of fact-checking a single claim."""

    claim: str
    verdict: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_summary: str
    sources: list[str]


class CheckResponse(BaseModel):
    """Full fact-check response returned to the client."""

    verdict: str
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    claim_results: list[ClaimResult]
    sources: list[str]
    processing_time_ms: int


class HealthResponse(BaseModel):
    """Health-check endpoint response."""

    status: str
    model: str
    corpus_size: int
