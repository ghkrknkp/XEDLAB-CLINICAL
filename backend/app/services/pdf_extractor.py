"""PDF text extraction. Uses PyMuPDF for selectable text; falls back to OCR
(via ocr_service) for scanned pages with no extractable text."""
from typing import List, Dict
import fitz  # PyMuPDF

from app.services.ocr_service import ocr_image_bytes

MIN_CHARS_FOR_SELECTABLE_TEXT = 20  # below this, treat page as "no text" -> OCR


def extract_pdf_pages(file_bytes: bytes) -> List[Dict]:
    """Returns a list of {page, text, ocr_used} dicts, one per PDF page.

    Never OCRs a page that already has selectable text (requirement #5).
    """
    pages: List[Dict] = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            text = page.get_text("text") or ""

            if len(text.strip()) >= MIN_CHARS_FOR_SELECTABLE_TEXT:
                pages.append({"page": page_index + 1, "text": text, "ocr_used": False})
                continue

            # No usable selectable text -> render page to image and OCR it.
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            ocr_text = ocr_image_bytes(img_bytes)
            pages.append({"page": page_index + 1, "text": ocr_text, "ocr_used": True})
    finally:
        doc.close()

    return pages
