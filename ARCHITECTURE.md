# AYUSHYA — Architecture & Data Model

## 1. System overview

```
        Official Sources
   (India Code, IP India, AYUSH,
    FSSAI, WIPO, CBD)
              │
              ▼
      Document Ingestion
 (PDF/HTML → clean → version → metadata)
              │
              ▼
        Knowledge Layer
 (Supabase: PostgreSQL + pgvector,
  legal_chunks, source metadata)
              │
              ▼
          RAG Engine
 (query routing → retrieval →
  reranking → evidence selection)
              │
              ▼
       LLM (Gemini / GPT)
              │
              ▼
     AYUSHYA Application
 (answer, citations, confidence,
  checklist, classification,
  multilingual, human escalation)
```

## 2. Storage layers (conceptual pipeline)

```
Source documents → Document repository → Extracted text
→ Structured chunks → Embeddings → Vector database → RAG
```

### 2.1 Raw document storage

Keep originals untouched, organized by jurisdiction and domain:

```
data/
└── raw/
    ├── india/
    │   ├── patents/
    │   │   ├── patents_act_1970.pdf
    │   │   └── patents_rules_2003.pdf
    │   ├── trademarks/
    │   ├── gi/
    │   ├── copyright/
    │   └── designs/
    └── international/
        ├── wipo/
        ├── trips/
        └── cbd/
```

Rule: never overwrite a file in `raw/`. A new version of a source gets a new dated file/entry, not an in-place edit.

### 2.2 Document-level metadata

Every ingested document gets a metadata record:

```json
{
  "document_id": "patents_act_1970",
  "title": "The Patents Act, 1970",
  "jurisdiction": "India",
  "document_type": "Act",
  "authority": "Government of India",
  "source": "India Code",
  "source_url": "...",
  "publication_date": "...",
  "effective_date": "...",
  "retrieved_at": "...",
  "version": "...",
  "sha256": "...",
  "status": "active"
}
```

### 2.3 Chunk-level schema

Don't store bare `{chunk_id, text, embedding}`. Store enough structure to produce a precise citation:

```json
{
  "chunk_id": "patents_1970_s3_c_001",
  "document_id": "patents_act_1970",
  "act_name": "Patents Act, 1970",
  "section": "Section 3",
  "subsection": "3(c)",
  "jurisdiction": "India",
  "text": "...",
  "source_url": "...",
  "page": 8
}
```

### 2.4 Supabase table map

```
documents            — one row per source document, metadata as in 2.2
document_versions    — historical versions of a document (effective_from/to, status)
legal_chunks          — chunk text + metadata (2.3) + embedding (pgvector)
sources               — canonical list of source sites (India Code, WIPO, etc.)
jurisdictions          — India / International / per-country if extended later
regulations           — structured regulatory items (for the Checklist module)
products              — user-submitted product/formulation records
conversations         — chat history
feedback              — user or reviewer feedback on answer quality
```

## 3. RAG pipeline (query-time flow)

```
User question
   → Language detection
   → Query understanding
   → Intent classification (e.g. "patentability", "labeling requirement")
   → Jurisdiction detection (explicit or inferred, never assumed silently)
   → Document/domain routing
   → Hybrid retrieval (vector + keyword/metadata filter)
   → Reranking
   → Evidence selection
   → LLM reasoning (grounded strictly in selected evidence)
   → Answer validation (citation check, no-fabrication check)
   → Citation generation
   → Response
```

Example trace for *"Can I patent my herbal formulation?"*:
- Intent: patentability
- Domain: Patent + Traditional Knowledge
- Jurisdiction: India
- Retrieval targets: Patents Act, Patent Rules, relevant IP India material, traditional-knowledge/prior-art resources, biodiversity/ABS sources where applicable

## 4. Document versioning

Laws change — never treat a source PDF as permanent truth.

```
Patents Act
├── Version 2024
├── Version 2025
└── Version 2026
```

Each version carries `effective_from`, `effective_to`, `status`, `retrieved_at`, `source_url`, `hash`. Retrieval should default to the current-status version unless a query explicitly asks about a historical position.

## 5. Tech stack (matches existing toolset)

- **Frontend:** React/Next.js + TypeScript + Tailwind
- **Backend/DB:** Supabase (PostgreSQL + pgvector, RLS for user data)
- **LLM:** Gemini or GPT-4o-mini via API (swap-able — don't hardcode a single provider deep in the app)
- **Embeddings:** Gemini text-embedding-004 or OpenAI text-embedding-3-small
- **Ingestion scripts:** Python (requests/BeautifulSoup for scraping where applicable, pypdf for text extraction)

## 6. Related documents
- `PRD.md` — product scope and modules
- `RULES.md` — hard rules this architecture must uphold
- `AGENTS.md` — instructions for AI coding agents working in this repo
