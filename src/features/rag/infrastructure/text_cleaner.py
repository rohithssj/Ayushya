import re
from typing import List, Tuple

class TextCleaner:
    """Cleans extracted text while retaining line and page boundaries for chunking."""

    def clean_pages(self, pages_data: List[Tuple[int, str]], start_page: int = 1) -> List[Tuple[int, str]]:
        cleaned_lines: List[Tuple[int, str]] = []

        for page_num, raw_text in pages_data:
            if page_num < start_page:
                continue

            lines = raw_text.split('\n')
            for line in lines:
                l_str = line.strip()
                if not l_str:
                    continue

                # Strip standalone page numbers at page headers/footers
                if l_str.isdigit() and len(l_str) <= 3:
                    continue

                if l_str.lower() in {"indiacode", "india code"}:
                    continue

                # Filter out legislative amendment footnotes (e.g. "1. Subs. by Act...", "2. Ins. by...", "3. Omitted by...")
                if re.match(r'^\d+[\.\*\[\]\s]+(?:Subs\.|Ins\.|Omitted|Certain|Sub-clause|Cl\.|The proviso|Sub-section|Added|Re-numbered|Restored)', l_str, re.IGNORECASE):
                    continue

                # Filter out footnote date stamps e.g. "(w.e.f. 20-5-2003)"
                if re.search(r'\(w\.e\.f\.\s+\d+[\-\/]\d+[\-\/]\d+\)', l_str):
                    continue

                # Filter out asterisk divider lines e.g. "1* * * * *"
                if re.match(r'^\d+\*\s+\*\s+\*', l_str):
                    continue

                # Normalize whitespace and dash variants without joining legal clauses.
                l_str = l_str.replace('\u2014', '-').replace('\u2013', '-').replace('\u201c', '"').replace('\u201d', '"')
                l_str = re.sub(r'\s+', ' ', l_str).strip()
                cleaned_lines.append((page_num, l_str))

        return cleaned_lines
