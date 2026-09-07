# AYUSHYA

AI-Powered IP & Regulatory Intelligence for Ayurveda.

## Status

**Structure-only scaffold.** Per `AGENTS.md` and the master structure prompt,
no business features are implemented yet. The folder structure, documentation
contract, and dependency boundaries are in place; feature implementation will
happen incrementally after approval.

## Start here

- `PRD.md` — product scope and MVP modules
- `RULES.md` — hard development/safety rules
- `ARCHITECTURE.md` — data model, storage layers, RAG pipeline
- `AGENTS.md` — instructions for AI coding agents

## Architecture summary

- **Feature-based + 4-layer** (Presentation → Application → Domain → Infrastructure).
- See `docs/architecture/LAYERS.md` (placeholder; created during structure setup).
- Each `src/features/<feature>/` owns its own presentation/, application/,
  domain/, infrastructure/, tests/ subfolders. Shared code lives under
  `src/shared/` only when genuinely shared.

## Tech stack (locked by `ARCHITECTURE.md` §5)

- Next.js (App Router) + React + TypeScript
- Tailwind CSS
- Supabase (PostgreSQL + pgvector, RLS for user data)
- LLM: Gemini or GPT-4o-mini via API (swap-able provider)
- Embeddings: Gemini text-embedding-004 or OpenAI text-embedding-3-small
- Ingestion scripts: Python

## Local development

```bash
cp .env.example .env.local   # fill placeholders
npm install
npm run dev
```

Validation commands (run after edits):

```bash
npm run typecheck
npm run lint
npm test
npm run build
```