import os
from typing import List, Tuple
import pypdf


class PdfExtractor:
    """Extract raw text with an OCR fallback for image-only PDF pages."""

    def __init__(self, ocr_scale: float = 1.0) -> None:
        self.warnings: List[str] = []
        self.ocr_pages: List[int] = []
        self.ocr_failures: List[int] = []
        self.ocr_scale = ocr_scale

    def extract_pages(self, pdf_path: str) -> List[Tuple[int, str]]:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")

        reader = pypdf.PdfReader(pdf_path)
        pages_data: List[Tuple[int, str]] = []
        self.warnings = []
        self.ocr_pages = []
        self.ocr_failures = []
        ocr_document = None
        ocr_engine = None
        ocr_attempted = False

        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            extracted = page.extract_text() or ""
            if not extracted.strip():
                if not ocr_attempted:
                    ocr_document, ocr_engine = self._load_ocr(pdf_path)
                    ocr_attempted = True
                if ocr_document is not None and ocr_engine is not None:
                    extracted = self._extract_ocr_page(
                        ocr_document, ocr_engine, page_num
                    )
                    if extracted.strip():
                        self.ocr_pages.append(page_num)
                    else:
                        self.ocr_failures.append(page_num)
                else:
                    self.ocr_failures.append(page_num)
                if not extracted.strip():
                    self.warnings.append(f"Page {page_num} contained no extractable text")
            pages_data.append((page_num, extracted))

        if ocr_document is not None:
            ocr_document.close()
        return pages_data

    def _load_ocr(self, pdf_path: str):
        try:
            import numpy as np
            import pymupdf
            from rapidocr_onnxruntime import RapidOCR
        except ImportError as error:
            self.warnings.append(
                "OCR fallback unavailable; install PyMuPDF and rapidocr_onnxruntime"
            )
            return None, None

        return pymupdf.open(pdf_path), RapidOCR()

    def _extract_ocr_page(self, document, ocr_engine, page_num: int) -> str:
        import numpy as np
        import pymupdf

        page = document[page_num - 1]
        scale = self.ocr_scale if len(document) <= 20 else min(self.ocr_scale, 0.5)
        pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
        image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
            pixmap.height, pixmap.width, pixmap.n
        )
        result, _ = ocr_engine(image)
        if not result:
            return ""
        return "\n".join(str(row[1]) for row in result if len(row) > 1 and row[1])
