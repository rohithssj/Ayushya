# AYUSHYA — Development Rules

These are hard requirements, not suggestions. Any code, prompt, or feature that
violates one of these should be treated as a bug, regardless of how well it demos.

## Product-level rules

1. AYUSHYA is an AI decision-support system, not a lawyer. Never phrase output as legal advice.
2. All important legal/regulatory claims must be backed by retrieved, authoritative evidence — never by the LLM's general/parametric knowledge.
3. Never fabricate laws, sections, cases, treaties, regulations, or citations. If it wasn't retrieved, it doesn't get cited.
4. Prefer official government/international sources over secondary material (see source hierarchy below).
5. If evidence is insufficient to answer confidently, the system must say so and abstain rather than guess.
6. Show a confidence/evidence-strength indicator on every substantive answer.
7. Product classification is preliminary AI assistance, not an official regulatory determination — label it as such every time it's shown.
8. Never guarantee patent approval or regulatory approval. "Potentially relevant" / "may apply", never "will".
9. Never silently mix Indian and international law in one answer — jurisdiction must be explicit.
10. Prefer the latest verified applicable version of a source; flag when a cited source may be outdated.
11. Human escalation must exist and be offered for uncertain or high-risk cases.

## Data & storage rules

12. Every document must have provenance metadata (source, URL, retrieval date, jurisdiction, document type, authority).
13. Every document must be versioned. Never overwrite a source file — add a new dated version instead.
14. Never modify original raw documents — keep `raw/` immutable; all cleaning/processing happens on copies.
15. Store section/chapter/subsection metadata on chunks whenever the source structure allows it, not just a text blob.
16. Store source URL and jurisdiction on every retrievable chunk — this is what makes citations possible.
17. Keep raw documents, processed/cleaned text, and embeddings as separate layers/tables, not conflated.

## Source priority hierarchy

When multiple sources exist for a claim, prefer in this order:

1. **Level 1 — Authoritative:** Acts, Rules, Regulations, official government notifications, official treaties, official government databases
2. **Level 2 — Official explanatory material:** government guidelines, official FAQs, manuals, circulars
3. **Level 3 — Secondary:** academic papers, law-firm articles, research papers, news, blogs

Never use a Level-3 source as the sole basis for a critical legal claim if a Level-1 source exists for the same point.

## AI / RAG behavior rules

18. RAG first — no LLM training/fine-tuning required or expected for this MVP.
19. Every AI response must be traceable to specific retrieved evidence (chunk-level, not just "the Patents Act somewhere").
20. Distinguish stated fact (from a source) from AI inference (e.g. "based on the classification above") — don't blend them without a marker.
21. Every major feature/answer type must be testable against a known question with a known expected authoritative source — treat this as a regression suite, not just a demo script.
22. Accuracy and citation correctness matter more than the number of documents in the database. A small, correct corpus beats a large, unverified one.

## Privacy & safety rules

23. Users may submit confidential formulation details — treat this as sensitive input.
24. Don't send more user information to an external LLM API than the task actually requires.
25. Don't log sensitive formulation text unnecessarily; don't use user input for any model training.
26. Encrypt data in transit; use authenticated database access; apply row-level security in Supabase where user-specific data exists.
27. Tell users plainly what happens to their data (even a one-line note in the UI is enough for MVP).

## Engineering separation of concerns

28. Keep ingestion, retrieval, reasoning (LLM prompting), and UI as separate layers/modules — don't hardcode retrieval logic into UI components or prompts into ingestion scripts.
