"""OCR fallback using Tesseract. Also handles direct image uploads (png/jpg)."""
import io
import shutil
from typing import List, Dict

from PIL import Image

from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

# Check if Tesseract is available on the system
_TESSERACT_AVAILABLE = shutil.which("tesseract") is not None

if _TESSERACT_AVAILABLE:
    import pytesseract
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    logger.info("Tesseract OCR is available.")
else:
    pytesseract = None
    logger.warning("Tesseract OCR is NOT installed. Image uploads will use Pillow fallback.")


def ocr_image_bytes(image_bytes: bytes) -> str:
    """Extract text from image bytes using Tesseract OCR."""
    if not _TESSERACT_AVAILABLE:
        logger.warning("OCR skipped — Tesseract not installed. Returning empty text.")
        return ""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Convert to grayscale for better OCR accuracy
        image = image.convert("L")
        text = pytesseract.image_to_string(image)
        logger.info("OCR extracted %d characters from image.", len(text))
        return text
    except Exception as exc:
        logger.error("OCR failed: %s", str(exc))
        return ""


def extract_image_pages(image_bytes: bytes) -> List[Dict]:
    """Extract text from a direct image upload (png/jpg/jpeg)."""
    text = ocr_image_bytes(image_bytes)
    if not text.strip():
        logger.warning("No text extracted from image. The report may appear empty.")
    return [{"page": 1, "text": text, "ocr_used": True}]


def extract_txt_pages(file_bytes: bytes) -> List[Dict]:
    """Extract text from a plain-text file."""
    text = file_bytes.decode("utf-8", errors="ignore")
    return [{"page": 1, "text": text, "ocr_used": False}]
