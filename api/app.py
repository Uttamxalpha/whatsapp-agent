import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import router as api_router
from api.middleware import (
    RequestLoggingMiddleware,
    ocr_failed_handler,
    no_claims_handler,
    llm_error_handler,
    generic_error_handler,
)
from core.exceptions import OCRFailedError, NoClaimsFoundError, LLMError
from rag.corpus_loader import load_corpus

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: load corpus on startup."""
    corpus_size = load_corpus()
    logger.info("Application started, corpus_size=%d", corpus_size)
    yield
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="Misinfo Buster",
        description="WhatsApp Misinformation Fact-Checker API powered by LangGraph and Groq",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    app.add_exception_handler(OCRFailedError, ocr_failed_handler)
    app.add_exception_handler(NoClaimsFoundError, no_claims_handler)
    app.add_exception_handler(LLMError, llm_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    app.include_router(api_router, prefix="/api/v1")

    return app
