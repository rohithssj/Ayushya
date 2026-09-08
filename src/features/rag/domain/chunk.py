from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class DocumentMetadata:
    document_id: str
    title: str
    jurisdiction: str
    domain: str
    document_type: str
    authority: str
    original_filename: str
    filename: str
    path: str
    year: Optional[int] = None
    ministry_department: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    language: str = "English"
    status: str = "active"
    parent_law: Optional[str] = None
    supersedes: Optional[str] = None
    retrieved_at: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class LegalChunk:
    chunk_id: str
    document_id: str
    title: str
    jurisdiction: str
    domain: str
    document_type: str
    authority: str
    source: Optional[str]
    source_url: Optional[str]
    year: Optional[int]
    language: str
    status: str
    retrieved_at: Optional[str]
    chapter: Optional[str]
    section: Optional[str]
    section_title: Optional[str]
    subsection: Optional[str]
    page: Optional[int]
    page_start: int
    page_end: int
    text: str
    char_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "title": self.title,
            "jurisdiction": self.jurisdiction,
            "domain": self.domain,
            "document_type": self.document_type,
            "authority": self.authority,
            "source": self.source,
            "source_url": self.source_url,
            "year": self.year,
            "language": self.language,
            "status": self.status,
            "retrieved_at": self.retrieved_at,
            "chapter": self.chapter,
            "section": self.section,
            "section_title": self.section_title,
            "subsection": self.subsection,
            "page": self.page,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "text": self.text,
            "char_count": self.char_count
        }
