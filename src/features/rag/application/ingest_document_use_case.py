import os
import json
from typing import Dict, Any, List, Optional
from src.features.rag.domain.chunk import DocumentMetadata, LegalChunk
from src.features.rag.infrastructure.pdf_extractor import PdfExtractor
from src.features.rag.infrastructure.text_cleaner import TextCleaner
from src.features.rag.infrastructure.legal_chunker import LegalChunker

class IngestDocumentUseCase:
    """Application use case for RAG Document Ingestion Phase 1."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.manifest_path = os.path.join(base_dir, "data", "metadata", "resource_manifest.json")
        self.processed_dir = os.path.join(base_dir, "data", "processed")
        self.extractor = PdfExtractor()
        self.cleaner = TextCleaner()
        self.chunker = LegalChunker()

    def execute(self, document_id: str, start_page: Optional[int] = None) -> Dict[str, Any]:
        metadata_dict = self._load_metadata(document_id)
        if not metadata_dict:
            raise ValueError(f"Document with ID '{document_id}' not found in manifest: {self.manifest_path}")

        meta = DocumentMetadata(**metadata_dict)
        full_pdf_path = os.path.join(self.base_dir, meta.path.replace("/", os.sep))

        # Step 1: Extract PDF pages
        raw_pages = self.extractor.extract_pages(full_pdf_path)
        total_pages = len(raw_pages)

        # Step 2: Clean lines
        effective_start_page = start_page or self._detect_content_start_page(raw_pages, meta.title)
        cleaned_lines = self.cleaner.clean_pages(raw_pages, start_page=effective_start_page)

        # Step 3: Chunk text with legal context
        chunks = self.chunker.chunk_document(meta, cleaned_lines)

        # Step 4: Save processed output
        os.makedirs(self.processed_dir, exist_ok=True)
        output_filename = f"{meta.document_id}_chunks.json"
        output_path = os.path.join(self.processed_dir, output_filename)

        dict_chunks = [c.to_dict() for c in chunks]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dict_chunks, f, indent=2, ensure_ascii=False)

        return {
            "document_id": meta.document_id,
            "title": meta.title,
            "pdf_path": meta.path,
            "total_pages": total_pages,
            "pages_processed": f"Pages {effective_start_page} to {total_pages}",
            "start_page": effective_start_page,
            "chunks_created": len(chunks),
            "output_file": os.path.join("data", "processed", output_filename),
            "extraction_warnings": self.extractor.warnings,
            "example_chunks": dict_chunks[:3]
        }

    @staticmethod
    def _detect_content_start_page(raw_pages: List[Any], title: str) -> int:
        for page_number, text in raw_pages:
            upper_text = text.upper()
            if "BE IT ENACTED" in upper_text:
                return page_number
        title_marker = title.upper()
        for page_number, text in raw_pages:
            upper_text = text.upper()
            if title_marker in upper_text and "CHAPTER I" in upper_text:
                return page_number
        return 1

    def _load_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Resource manifest not found at: {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        for item in manifest:
            if item.get("document_id") == document_id or item.get("filename") == document_id:
                return item

        return None
