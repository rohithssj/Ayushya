import re
from typing import Any, Dict, List, Optional, Tuple

from src.features.rag.domain.chunk import DocumentMetadata, LegalChunk


class LegalChunker:
    """Create chunks around statutory sections and their logical provisions."""

    section_re = re.compile(r"^[\s\[\]\*\$]*?(\d+[A-Z]?)\.\s*(.+)$", re.IGNORECASE)
    chapter_re = re.compile(r"^(CHAPTER\s+[IVXLCDM]+\b.*|PART\s+[IVXLCDM]+\b.*)$", re.IGNORECASE)
    schedule_re = re.compile(
        r"^(?:THE\s+)?(?:(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH)\s+)?SCHEDULE\b.*$",
        re.IGNORECASE,
    )
    clause_re = re.compile(r"^(?:\d+\[)?\(([0-9]+|[a-z]+|[ivxlcdm]+)\)\s+", re.IGNORECASE)

    def __init__(self, max_chunk_chars: int = 1800):
        self.max_chunk_chars = max_chunk_chars

    def chunk_document(
        self, metadata: DocumentMetadata, cleaned_lines: List[Tuple[int, str]]
    ) -> List[LegalChunk]:
        sections = self._parse_sections(cleaned_lines)
        if not sections and cleaned_lines:
            return self._chunk_unsectioned_document(metadata, cleaned_lines)

        chunks: List[LegalChunk] = []
        sequence = 1

        for section in sections:
            groups = self._group_units(section["lines"])
            for group in groups:
                subsection = self._subsection_label(group)
                section_number = section["section_number"]
                section_title = section["section_title"]
                context = (
                    f"[{metadata.title} | {section['chapter']} | "
                    f"Section {section_number} {section_title}]"
                )
                text = context + "\n" + "\n".join(line for _, line in group)
                chunks.append(
                    LegalChunk(
                        chunk_id=f"{metadata.document_id}_sec_{section_number}_{sequence:04d}",
                        document_id=metadata.document_id,
                        title=metadata.title,
                        jurisdiction=metadata.jurisdiction,
                        domain=metadata.domain,
                        document_type=metadata.document_type,
                        authority=metadata.authority,
                        source=metadata.source,
                        source_url=metadata.source_url,
                        year=metadata.year,
                        language=metadata.language,
                        status=metadata.status,
                        retrieved_at=metadata.retrieved_at,
                        chapter=section["chapter"],
                        section=f"Section {section_number}",
                        section_title=section_title,
                        subsection=subsection,
                        page=group[0][0] if group[0][0] == group[-1][0] else None,
                        page_start=group[0][0],
                        page_end=group[-1][0],
                        text=text,
                        char_count=len(text),
                    )
                )
                sequence += 1

        return chunks

    def _chunk_unsectioned_document(
        self, metadata: DocumentMetadata, cleaned_lines: List[Tuple[int, str]]
    ) -> List[LegalChunk]:
        """Chunk usable text when a document has no statutory headings."""

        chunks: List[LegalChunk] = []
        current: List[Tuple[int, str]] = []
        current_length = 0
        sequence = 1

        def flush() -> None:
            nonlocal sequence, current, current_length
            if not current:
                return
            page_start = current[0][0]
            page_end = current[-1][0]
            text = "\n".join(line for _, line in current)
            chunks.append(
                LegalChunk(
                    chunk_id=f"{metadata.document_id}_chunk_{sequence:04d}",
                    document_id=metadata.document_id,
                    title=metadata.title,
                    jurisdiction=metadata.jurisdiction,
                    domain=metadata.domain,
                    document_type=metadata.document_type,
                    authority=metadata.authority,
                    source=metadata.source,
                    source_url=metadata.source_url,
                    year=metadata.year,
                    language=metadata.language,
                    status=metadata.status,
                    retrieved_at=metadata.retrieved_at,
                    chapter=None,
                    section=None,
                    section_title=None,
                    subsection=None,
                    page=page_start if page_start == page_end else None,
                    page_start=page_start,
                    page_end=page_end,
                    text=text,
                    char_count=len(text),
                )
            )
            sequence += 1
            current = []
            current_length = 0

        for line in cleaned_lines:
            line_length = len(line[1]) + 1
            if current and current_length + line_length > self.max_chunk_chars:
                flush()
            current.append(line)
            current_length += line_length
        flush()
        return chunks

    def _parse_sections(self, cleaned_lines: List[Tuple[int, str]]) -> List[Dict[str, Any]]:
        sections: List[Dict[str, Any]] = []
        chapter = "UNSPECIFIED"
        current: Optional[Dict[str, Any]] = None
        in_contents = False
        in_schedule = False

        for page, line in cleaned_lines:
            if line.strip().lower() == "contents":
                in_contents = True
                continue

            if in_contents:
                if self._looks_like_document_body(line):
                    in_contents = False
                else:
                    continue

            chapter_match = self.chapter_re.match(line) or self.schedule_re.match(line)
            if chapter_match:
                chapter = line
                if current:
                    sections.append(current)
                    current = None
                in_schedule = bool(self.schedule_re.match(line))
                if in_schedule:
                    current = {
                        "chapter": chapter,
                        "section_number": "schedule",
                        "section_title": "Schedule",
                        "lines": [(page, line)],
                    }
                continue

            if in_schedule:
                if current:
                    current["lines"].append((page, line))
                continue

            section_match = self.section_re.match(line)
            if section_match and self._is_statutory_heading(section_match.group(2)):
                if current:
                    sections.append(current)
                section_number = section_match.group(1)
                heading = section_match.group(2).strip()
                title, provision = self._split_heading(heading)
                heading_line = f"{section_number}. {title}"
                if provision:
                    heading_line += f" - {provision}"
                current = {
                    "chapter": chapter,
                    "section_number": section_number,
                    "section_title": title,
                    "lines": [(page, heading_line)],
                }
                continue

            if current:
                current["lines"].append((page, line))

        if current:
            sections.append(current)
        return sections

    @staticmethod
    def _looks_like_document_body(line: str) -> bool:
        return bool(
            re.search(
                r"\b(?:notification|hereby|following|these rules|unless the context|be it enacted)\b",
                line,
                re.IGNORECASE,
            )
        )

    @staticmethod
    def _split_heading(heading: str) -> Tuple[str, str]:
        match = re.match(
            r"^(.*?)(?:\s*-\s*)(?=(?:\(|The\b|No\b|An\b|A\b|This\b|Any\b))(.+)$",
            heading,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).strip(" ."), match.group(2).strip()
        return heading.strip(), ""

    @staticmethod
    def _is_statutory_heading(heading: str) -> bool:
        lowered = heading.lower()
        rejected_markers = (
            "omitted by",
            "inserted by",
            "substituted by",
            "section 1-in ",
            "notes on clauses",
        )
        if any(marker in lowered for marker in rejected_markers):
            return False
        return not bool(re.search(r"\bvide\b|\bdt\.|w\.e\.f\.", lowered))

    def _group_units(self, units: List[Tuple[int, str]]) -> List[List[Tuple[int, str]]]:
        if not units:
            return []
        groups: List[List[Tuple[int, str]]] = []
        current: List[Tuple[int, str]] = []
        current_length = 0
        for unit in units:
            unit_length = len(unit[1]) + 1
            starts_clause = bool(self.clause_re.match(unit[1]))
            if current and starts_clause and current_length + unit_length > self.max_chunk_chars:
                groups.append(current)
                current = []
                current_length = 0
            current.append(unit)
            current_length += unit_length
        if current:
            groups.append(current)
        return groups

    def _subsection_label(self, group: List[Tuple[int, str]]) -> Optional[str]:
        labels = []
        for _, line in group:
            match = self.clause_re.match(line) or re.search(
                r"(?:^|\s|\[)(\([0-9a-z]+\))\s+", line, re.IGNORECASE
            )
            if match:
                label = match.group(1)
                labels.append(label if label.startswith("(") else f"({label})")
        if not labels:
            return None
        return labels[0] if len(labels) == 1 else f"{labels[0]}-{labels[-1]}"
