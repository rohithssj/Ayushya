import unittest
import tempfile
from unittest.mock import MagicMock, patch

from src.features.rag.infrastructure.pdf_extractor import PdfExtractor


class PdfExtractorTests(unittest.TestCase):
    @patch("src.features.rag.infrastructure.pdf_extractor.pypdf.PdfReader")
    def test_uses_ocr_for_pages_without_text(self, reader_mock):
        text_page = type("Page", (), {"extract_text": lambda self: "Native text"})()
        image_page = type("Page", (), {"extract_text": lambda self: ""})()
        reader_mock.return_value.pages = [text_page, image_page]
        ocr_document = MagicMock()

        with tempfile.NamedTemporaryFile(suffix=".pdf") as fixture, patch.object(
            PdfExtractor, "_load_ocr", return_value=(ocr_document, object())
        ), patch.object(PdfExtractor, "_extract_ocr_page", return_value="OCR text") as ocr_page:
            pages = PdfExtractor().extract_pages(fixture.name)

        self.assertEqual(pages, [(1, "Native text"), (2, "OCR text")])
        self.assertEqual(ocr_page.call_count, 1)

    @patch("src.features.rag.infrastructure.pdf_extractor.pypdf.PdfReader")
    def test_records_warning_when_ocr_is_unavailable(self, reader_mock):
        image_page = type("Page", (), {"extract_text": lambda self: ""})()
        reader_mock.return_value.pages = [image_page]

        with tempfile.NamedTemporaryFile(suffix=".pdf") as fixture, patch.object(
            PdfExtractor, "_load_ocr", return_value=(None, None)
        ):
            extractor = PdfExtractor()
            pages = extractor.extract_pages(fixture.name)

        self.assertEqual(pages, [(1, "")])
        self.assertEqual(extractor.ocr_failures, [1])
        self.assertIn("Page 1 contained no extractable text", extractor.warnings)


if __name__ == "__main__":
    unittest.main()