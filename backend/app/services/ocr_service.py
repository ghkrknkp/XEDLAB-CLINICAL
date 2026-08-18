"""OCR fallback using Tesseract. Also handles direct image uploads (png/jpg)."""
import io
from typing import List, Dict

import pytesseract
from PIL import Image

from app.core.config import get_settings

settings = get_settings()
if settings.tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


def ocr_image_bytes(image_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Light preprocessing: convert to grayscale, which generally improves
        # OCR accuracy on scanned documents without risking artifact-introducing
        # aggressive filters.
        image = image.convert("L")
        text = pytesseract.image_to_string(image)
        return text
    except Exception as exc:  # pragma: no cover - defensive, tesseract may be missing
        # Never crash the pipeline because OCR isn't installed; degrade gracefully.
        return ""


def extract_image_pages(image_bytes: bytes) -> List[Dict]:
    text = ocr_image_bytes(image_bytes)
    return [{"page": 1, "text": text, "ocr_used": True}]


def extract_txt_pages(file_bytes: bytes) -> List[Dict]:
    text = file_bytes.decode("utf-8", errors="ignore")
    return [{"page": 1, "text": text, "ocr_used": False}]
