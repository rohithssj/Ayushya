import os
from typing import List, Tuple
import pypdf

class PdfExtractor:
    """Extracts raw text page-by-page from legal PDFs."""

    def __init__(self) -> None:
        self.warnings: List[str] = []

    def extract_pages(self, pdf_path: str) -> List[Tuple[int, str]]:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")

        reader = pypdf.PdfReader(pdf_path)
        pages_data: List[Tuple[int, str]] = []
        self.warnings = []

        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            extracted = page.extract_text() or ""
            if not extracted.strip():
                self.warnings.append(f"Page {page_num} contained no extractable text")
            pages_data.append((page_num, extracted))

        return pages_data
