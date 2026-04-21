class OCRFailedError(Exception):
    """Raised when OCR text extraction fails."""
    pass


class NoClaimsFoundError(Exception):
    """Raised when no verifiable claims are found in the input."""
    pass


class SearchFailedError(Exception):
    """Raised when web search fails."""
    pass


class LLMError(Exception):
    """Raised when the LLM service encounters an error."""
    pass


class ChromaError(Exception):
    """Raised when ChromaDB operations fail."""
    pass
