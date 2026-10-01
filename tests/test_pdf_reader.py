"""PDF fixture coverage and text-only rejection checks."""
import io
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from tender_clarity.pdf_reader import PDFInputError, extract_pages

ROOT = Path(__file__).resolve().parents[1]


class PDFReaderTests(unittest.TestCase):
    def test_fixture_has_repeatable_required_examples_across_two_pages(self):
        payload = (ROOT / "fixtures" / "synthetic_cleaning_tender.pdf").read_bytes()
        pages = extract_pages("synthetic_cleaning_tender.pdf", payload)
        self.assertEqual(len(pages), 2)
        page1, page2 = " ".join(pages[0].text.split()), " ".join(pages[1].text.split())
        self.assertIn("Failure to include the tax-compliance evidence makes the bid non-responsive", page1)
        self.assertIn("closing deadline is 30 October 2026 at 11:00", page1)
        self.assertIn("Price is worth 80 points", page1)
        self.assertIn("No list of items, quantities, or supply dates is provided", page2)
        self.assertIn("monthly service price", page2)
        self.assertIn("according to the weekend coverage in clause 8", page1)
        self.assertIn("two cleaners from 08:00 to 16:00", page2)

    def test_image_only_pdf_is_rejected_with_explanation(self):
        image_buffer = io.BytesIO()
        image = Image.new("RGB", (500, 80), "white")
        ImageDraw.Draw(image).text((10, 20), "Scanned tender text", fill="black")
        image.save(image_buffer, format="PNG")
        pdf_buffer = io.BytesIO()
        doc = canvas.Canvas(pdf_buffer)
        doc.drawImage(ImageReader(io.BytesIO(image_buffer.getvalue())), 30, 700, width=400, height=64)
        doc.save()
        with self.assertRaisesRegex(PDFInputError, "scanned images.*does not use OCR"):
            extract_pages("scan.pdf", pdf_buffer.getvalue())

    def test_size_limit_is_checked_before_parsing(self):
        from tender_clarity.pdf_reader import MAX_BYTES
        with self.assertRaisesRegex(PDFInputError, "20 MB limit"):
            extract_pages("large.pdf", b"%PDF-" + b"x" * MAX_BYTES)


    def test_page_limit_is_enforced(self):
        from tender_clarity.pdf_reader import MAX_PAGES
        pdf_buffer = io.BytesIO()
        doc = canvas.Canvas(pdf_buffer)
        for page_number in range(MAX_PAGES + 1):
            doc.drawString(40, 760, f"Selectable text on page {page_number + 1}")
            doc.showPage()
        doc.save()
        with self.assertRaisesRegex(PDFInputError, "100-page limit"):
            extract_pages("long.pdf", pdf_buffer.getvalue())

if __name__ == "__main__":
    unittest.main()

