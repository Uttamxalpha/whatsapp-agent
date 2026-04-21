import base64
import io
import logging
from typing import Optional

import numpy as np
from PIL import Image

from core.exceptions import OCRFailedError

logger = logging.getLogger(__name__)

_reader: Optional[object] = None


def _get_reader() -> object:
    """Lazy-load EasyOCR reader on first call to avoid slow import-time init."""
    global _reader
    if _reader is None:
        import easyocr
        logger.info("Initializing EasyOCR reader for languages: en, hi")
        _reader = easyocr.Reader(["en", "hi"], gpu=False)
    return _reader


def extract_text_from_base64(base64_str: str) -> str:
    """Decode a base64-encoded image and extract text via OCR."""
    try:
        image_bytes = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_array = np.array(image)
        reader = _get_reader()
        results: list[str] = reader.readtext(img_array, detail=0)
        extracted = " ".join(results).strip()
        logger.info("OCR extracted %d characters from base64 image", len(extracted))
        return extracted
    except Exception as exc:
        logger.error("OCR failed on base64 image: %s", exc)
        raise OCRFailedError(f"Failed to extract text from image: {exc}") from exc


def extract_text_from_path(file_path: str) -> str:
    """Read an image from disk and extract text via OCR."""
    try:
        image = Image.open(file_path).convert("RGB")
        img_array = np.array(image)
        reader = _get_reader()
        results: list[str] = reader.readtext(img_array, detail=0)
        extracted = " ".join(results).strip()
        logger.info("OCR extracted %d characters from file %s", len(extracted), file_path)
        return extracted
    except Exception as exc:
        logger.error("OCR failed on file %s: %s", file_path, exc)
        raise OCRFailedError(f"Failed to extract text from {file_path}: {exc}") from exc
