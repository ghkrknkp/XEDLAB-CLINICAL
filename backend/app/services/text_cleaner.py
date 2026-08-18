"""Text cleaning & normalization.

Deliberately conservative: we normalize whitespace/line breaks and strip common
OCR noise characters, but we never spell-correct medical terms or units, since
that risks silently corrupting values like 'mg/dL' -> a wrong unit.
"""
import re

# Characters that occasionally show up as OCR noise around numbers/units and
# are safe to strip without touching real content.
_NOISE_CHARS = re.compile(r"[\u2022\u25aa\u2013\u2014]")  # bullets, en/em dash artifacts
_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_MULTI_BLANK_LINES = re.compile(r"\n{3,}")


def clean_text(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Normalize dash-like OCR noise to a plain hyphen (kept, since ranges use it,
    # e.g. "12 - 16"), but never touch alphanumeric unit tokens.
    text = _NOISE_CHARS.sub("-", text)

    # Collapse repeated spaces/tabs but preserve line structure (important for
    # tabular lab report layouts).
    text = _MULTI_SPACE.sub(" ", text)
    text = _MULTI_BLANK_LINES.sub("\n\n", text)

    # Trim trailing whitespace per line.
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()


def clean_pages(pages: list) -> list:
    """Applies clean_text to each page dict's 'text' field, preserving page and
    ocr_used metadata."""
    cleaned = []
    for p in pages:
        cleaned.append({
            "page": p["page"],
            "text": clean_text(p["text"]),
            "ocr_used": p.get("ocr_used", False),
        })
    return cleaned
