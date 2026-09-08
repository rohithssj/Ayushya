import os
import pypdf
import re
import json

pdf_path = r"d:\SIH\data\raw\legal\india\patents\patents_act_1970.pdf"
reader = pypdf.PdfReader(pdf_path)

body_pages = []
for p_idx in range(8, len(reader.pages)):
    body_pages.append((p_idx + 1, reader.pages[p_idx].extract_text()))

cleaned_lines = []
for pg, text in body_pages:
    lines = text.split('\n')
    for l in lines:
        l_str = l.strip()
        if not l_str:
            continue
        if l_str.isdigit() and len(l_str) <= 3:
            continue
        if re.match(r'^\d+[\.\*\[\]\s]+(?:Subs\.|Ins\.|Omitted|Certain|Sub-clause|Cl\.|The proviso|Sub-section|Added|Re-numbered|Restored)', l_str, re.IGNORECASE):
            continue
        if re.search(r'\(w\.e\.f\.\s+\d+[\-\/]\d+[\-\/]\d+\)', l_str):
            continue
        if re.match(r'^\d+\*\s+\*\s+\*', l_str):
            continue
        cleaned_lines.append((pg, l_str))

# Parse Chapters and Sections
sections = []
curr_chapter = "CHAPTER I PRELIMINARY"
curr_sec_num = None
curr_sec_title = None
curr_lines = []
curr_pages = []

sec_heading_re = re.compile(r'^(\d+[A-Z]?)\.\s+([A-Z0-9\s,–\-—\'()\/\.\?\:\;\–\─]+?\.)\s*(.*)', re.IGNORECASE)

for pg, line in cleaned_lines:
    if line.startswith("CHAPTER ") or line.startswith("THE FIRST SCHEDULE") or line.startswith("THE SECOND SCHEDULE"):
        curr_chapter = line
    
    sec_m = sec_heading_re.match(line)
    is_footnote = False
    if sec_m:
        num = sec_m.group(1)
        title = sec_m.group(2).strip()

        if re.search(r'(?:w\.e\.f\.|ins\.\s+by|subs\.\s+by|omitted\s+by|ibid|s\.\s+\d+)', title, re.IGNORECASE):
            is_footnote = True

        if not is_footnote:
            if curr_lines and curr_sec_num:
                sections.append({
                    "chapter": curr_chapter,
                    "section_num": curr_sec_num,
                    "section_title": curr_sec_title,
                    "text": "\n".join(curr_lines),
                    "page_start": min(curr_pages),
                    "page_end": max(curr_pages)
                })
            curr_sec_num = num
            curr_sec_title = title
            curr_lines = [line]
            curr_pages = [pg]
            continue

    if curr_sec_num:
        curr_lines.append(line)
        curr_pages.append(pg)

if curr_lines and curr_sec_num:
    sections.append({
        "chapter": curr_chapter,
        "section_num": curr_sec_num,
        "section_title": curr_sec_title,
        "text": "\n".join(curr_lines),
        "page_start": min(curr_pages),
        "page_end": max(curr_pages)
    })

# Now perform section-aware chunking
doc_metadata = {
    "document_id": "india_patents_act_1970",
    "title": "The Patents Act, 1970",
    "jurisdiction": "India",
    "domain": "patents",
    "document_type": "Act",
    "authority": "Parliament of India",
    "source_url": "https://www.indiacode.nic.in"
}

chunks = []
chunk_index = 1

for sec in sections:
    text = sec["text"]
    sec_num = sec["section_num"]
    sec_title = sec["section_title"]
    chapter = sec["chapter"]
    p_start = sec["page_start"]
    p_end = sec["page_end"]

    # Check if section text is short/medium (<= 1500 chars)
    if len(text) <= 1500:
        chunk_id = f"{doc_metadata['document_id']}_sec_{sec_num}_{chunk_index:03d}"
        chunks.append({
            "chunk_id": chunk_id,
            "document_id": doc_metadata["document_id"],
            "title": doc_metadata["title"],
            "jurisdiction": doc_metadata["jurisdiction"],
            "domain": doc_metadata["domain"],
            "document_type": doc_metadata["document_type"],
            "authority": doc_metadata["authority"],
            "source_url": doc_metadata["source_url"],
            "chapter": chapter,
            "section": f"Section {sec_num}",
            "section_title": sec_title,
            "subsection": None,
            "page_start": p_start,
            "page_end": p_end,
            "text": text,
            "char_count": len(text)
        })
        chunk_index += 1
    else:
        # Split large section into logical subsections or clauses
        # Find clause/subsection splits e.g. "\n(a) ", "\n(1) ", "\n(i) "
        splits = re.split(r'\n(?=\([0-9a-z]+\)\s+)', text)
        if len(splits) > 1:
            for s_idx, part in enumerate(splits):
                if not part.strip(): continue
                sub_match = re.match(r'^\(([0-9a-z]+)\)', part.strip())
                sub_label = f"({sub_match.group(1)})" if sub_match else f"Part {s_idx+1}"
                
                # Contextual header prefix
                prefix = f"[{doc_metadata['title']} | {chapter} | Section {sec_num} {sec_title} {sub_label}]\n"
                full_text = prefix + part.strip()
                chunk_id = f"{doc_metadata['document_id']}_sec_{sec_num}_{s_idx+1:02d}_{chunk_index:03d}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_metadata["document_id"],
                    "title": doc_metadata["title"],
                    "jurisdiction": doc_metadata["jurisdiction"],
                    "domain": doc_metadata["domain"],
                    "document_type": doc_metadata["document_type"],
                    "authority": doc_metadata["authority"],
                    "source_url": doc_metadata["source_url"],
                    "chapter": chapter,
                    "section": f"Section {sec_num}",
                    "section_title": sec_title,
                    "subsection": sub_label,
                    "page_start": p_start,
                    "page_end": p_end,
                    "text": full_text,
                    "char_count": len(full_text)
                })
                chunk_index += 1
        else:
            # Fallback block split
            paras = text.split("\n\n")
            curr_chunk_text = f"[{doc_metadata['title']} | {chapter} | Section {sec_num} {sec_title}]\n"
            for para in paras:
                if len(curr_chunk_text) + len(para) > 1500:
                    chunk_id = f"{doc_metadata['document_id']}_sec_{sec_num}_{chunk_index:03d}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "document_id": doc_metadata["document_id"],
                        "title": doc_metadata["title"],
                        "jurisdiction": doc_metadata["jurisdiction"],
                        "domain": doc_metadata["domain"],
                        "document_type": doc_metadata["document_type"],
                        "authority": doc_metadata["authority"],
                        "source_url": doc_metadata["source_url"],
                        "chapter": chapter,
                        "section": f"Section {sec_num}",
                        "section_title": sec_title,
                        "subsection": None,
                        "page_start": p_start,
                        "page_end": p_end,
                        "text": curr_chunk_text,
                        "char_count": len(curr_chunk_text)
                    })
                    chunk_index += 1
                    curr_chunk_text = f"[{doc_metadata['title']} | {chapter} | Section {sec_num} {sec_title}]\n" + para
                else:
                    curr_chunk_text += "\n" + para
            if curr_chunk_text.strip():
                chunk_id = f"{doc_metadata['document_id']}_sec_{sec_num}_{chunk_index:03d}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_metadata["document_id"],
                    "title": doc_metadata["title"],
                    "jurisdiction": doc_metadata["jurisdiction"],
                    "domain": doc_metadata["domain"],
                    "document_type": doc_metadata["document_type"],
                    "authority": doc_metadata["authority"],
                    "source_url": doc_metadata["source_url"],
                    "chapter": chapter,
                    "section": f"Section {sec_num}",
                    "section_title": sec_title,
                    "subsection": None,
                    "page_start": p_start,
                    "page_end": p_end,
                    "text": curr_chunk_text,
                    "char_count": len(curr_chunk_text)
                })
                chunk_index += 1

print(f"Total chunks created: {len(chunks)}")
print("\n--- SAMPLE CHUNK (Section 3) ---")
sec3_chunks = [c for c in chunks if "Section 3" in c["section"]]
for sc in sec3_chunks[:5]:
    print(json.dumps(sc, indent=2))
