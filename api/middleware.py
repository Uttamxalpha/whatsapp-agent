import logging
import time

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.exceptions import OCRFailedError, NoClaimsFoundError, LLMError

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs each request method, path, status, and duration."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request and log timing information."""
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        logger.info(
            "method=%s path=%s status=%d duration_ms=%d",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


async def ocr_failed_handler(request: Request, exc: OCRFailedError) -> JSONResponse:
    """Handle OCR failures with HTTP 422."""
    logger.error("OCR failed: %s", exc)
    return JSONResponse(
        status_code=422,
        content={"error": str(exc), "type": "OCRFailedError"},
    )


async def no_claims_handler(request: Request, exc: NoClaimsFoundError) -> JSONResponse:
    """Handle no-claims-found with HTTP 422."""
    logger.error("No claims found: %s", exc)
    return JSONResponse(
        status_code=422,
        content={"error": str(exc), "type": "NoClaimsFoundError"},
    )


async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    """Handle LLM service errors with HTTP 503."""
    logger.error("LLM error: %s", exc)
    return JSONResponse(
        status_code=503,
        content={"error": str(exc), "type": "LLMError"},
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler returning HTTP 500."""
    logger.error("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__},
    )
