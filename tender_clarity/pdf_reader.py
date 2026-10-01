"""PDF checks and in-memory page-by-page text extraction."""

from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader

MAX_BYTES = 20 * 1024 * 1024
MAX_PAGES = 100


class PDFInputError(ValueError):
    pass


@dataclass
class ExtractedPage:
    number: int
    text: str


def extract_pages(filename: str, payload: bytes) -> list[ExtractedPage]:
    if len(payload) > MAX_BYTES:
        raise PDFInputError("This PDF is over the 20 MB limit. Please choose a smaller file.")
    if not filename.lower().endswith(".pdf") or not payload.startswith(b"%PDF-"):
        raise PDFInputError("Please upload a valid PDF file.")
    try:
        reader = PdfReader(BytesIO(payload), strict=False)
        if reader.is_encrypted:
            raise PDFInputError("This PDF is encrypted. Please upload an unlocked PDF.")
        count = len(reader.pages)
        if count > MAX_PAGES:
            raise PDFInputError("This PDF has more than the 100-page limit. Please choose a shorter document.")
        if count == 0:
            raise PDFInputError("This PDF has no pages to analyse.")
        pages = [ExtractedPage(i + 1, (page.extract_text() or "").strip()) for i, page in enumerate(reader.pages)]
    except PDFInputError:
        raise
    except Exception as exc:
        raise PDFInputError("Tender Clarity could not read this PDF. It may be damaged or use unsupported encoding.") from exc
    if not any(p.text for p in pages):
        raise PDFInputError("This PDF appears to contain scanned images rather than selectable text. Tender Clarity V1 cannot read it and does not use OCR. Please choose a text-based PDF.")
    return pages


def page_text_for_analysis(pages: list[ExtractedPage]) -> str:
    return "\n\n".join(f"[PAGE {p.number}]\n{p.text if p.text else '[No selectable text on this page]'}" for p in pages)
