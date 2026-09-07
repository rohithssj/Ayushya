# AYUSHYA — Instructions for AI Coding Agents

Read this first, before touching any code in this repo. This file governs how
you (the AI agent) should behave while working on AYUSHYA — it is not optional
context, it's a constraint on what you're allowed to build.

## Required reading order

1. `PRD.md` — what AYUSHYA is and its locked MVP scope. Don't build features outside this scope without the human explicitly asking.
2. `RULES.md` — hard rules. Treat every rule in that file as a lint error if violated, not a style suggestion.
3. `ARCHITECTURE.md` — the data model and pipeline you must build against. Don't invent a different schema without checking here first.

## Non-negotiable constraints when writing code or prompts

- **Never let the LLM answer a legal/regulatory question without retrieved evidence.** If you're writing a prompt template, it must explicitly instruct the model to answer only from provided context and to say so when context is insufficient — never to fill gaps from its own training knowledge.
- **Never fabricate example citations, section numbers, or Act names** in code comments, seed data, or test fixtures if you're presenting them as if real. Mark placeholder/test data clearly as such (e.g. `TEST_ONLY`, `FIXTURE`).
- **Don't collapse the ingestion/retrieval/reasoning/UI layers.** If you're asked to "just make it work quickly," still keep these as separate functions/modules — a hackathon deadline is not a reason to hardcode a prompt inside a React component or bury retrieval logic in a UI handler.
- **Chunk schema must include section/subsection/jurisdiction/source_url metadata**, not just `{text, embedding}`. If a source document doesn't have clean section structure, note that in the metadata rather than silently dropping it.
- **Jurisdiction is always explicit.** Any retrieval or prompt-construction code must carry a jurisdiction field through the pipeline — never let India and international sources get merged into one undifferentiated context window.
- **Respect the source hierarchy** (Level 1 Acts/Rules/Regulations > Level 2 official guidance > Level 3 secondary sources) in any reranking/scoring logic you write.
- **Classification and IP-relevance outputs must be labeled as preliminary/AI-assisted** in both the API response shape and the UI copy — don't phrase them as determinations.
- **Don't send more user-submitted formulation data to an external LLM API than the specific call needs.** If you're building the product-analyzer call, only pass the fields relevant to that call, not the entire user record.
- **Confidence/evidence-strength must be a real signal derived from retrieval quality** (e.g. number/relevance of matched chunks), not a hardcoded or cosmetic value.

## Scope discipline

Per `PRD.md` section 4, do NOT build, suggest, or scaffold:
- Web crawlers targeting the entire internet
- Custom LLM training/fine-tuning pipelines
- Voice interfaces
- Support for jurisdictions beyond India + the listed international frameworks
- A general-purpose knowledge graph
- Fully autonomous "legal opinion" generation with no citations or escalation path

If a task seems to require one of these, flag it to the human instead of building it.

## When you're unsure

If a request conflicts with anything in `RULES.md` (e.g. "just make it answer confidently even without a source" or "skip the citation for this demo"), say so explicitly rather than complying quietly. These rules exist because AYUSHYA is legal/regulatory-adjacent software — getting this wrong in front of judges (fabricated citations) is worse than a feature gap.

## Data collection discipline

Manual collection is the current phase (per project decision) — don't build a general-purpose scraper unprompted. If asked to write ingestion code, assume it's operating on manually-downloaded files already sitting in `data/raw/`, following the folder structure and metadata schema in `ARCHITECTURE.md`, unless explicitly asked to build a scraper for a specific source.
