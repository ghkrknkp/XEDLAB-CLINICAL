from app.services.pdf_extractor import extract_pdf_pages
import fitz


def _make_text_pdf_bytes(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_ocr_not_used_for_selectable_text_pdf():
    pdf_bytes = _make_text_pdf_bytes("Hemoglobin 10.2 g/dL 12.0-16.0 reference range test content here")
    pages = extract_pdf_pages(pdf_bytes)
    assert len(pages) == 1
    assert pages[0]["ocr_used"] is False
    assert "Hemoglobin" in pages[0]["text"]


def test_ocr_fallback_triggers_for_blank_page():
    doc = fitz.open()
    doc.new_page()  # blank page -> no selectable text -> should attempt OCR
    pdf_bytes = doc.tobytes()
    doc.close()

    pages = extract_pdf_pages(pdf_bytes)
    assert len(pages) == 1
    assert pages[0]["ocr_used"] is True
