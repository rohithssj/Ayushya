# AYUSHYA — Product Requirements Document

**Problem Statement:** SIH26045 (IP-SAKTI Sahayak), Ministry of Ayush
**Project name:** AYUSHYA — AI-Powered IP & Regulatory Intelligence for Ayurveda

---

## 1. One-line summary

AYUSHYA is a multilingual, source-cited AI assistant that helps Ayurveda innovators, researchers, startups, and practitioners understand which intellectual-property protections and regulatory requirements may apply to their product or formulation, grounded entirely in authoritative Indian and international sources.

## 2. Core workflow

```
User describes product/formulation
              ↓
      AYUSHYA asks clarifying questions
              ↓
       Product classification
              ↓
  IP identification + Regulatory identification
              ↓
        Retrieve legal sources (RAG)
              ↓
            AI reasoning
              ↓
  Answer + Sources + Confidence + Checklist
```

Example: *"I developed an Ayurvedic herbal formulation for diabetes using five herbs. Can I patent it?"* — AYUSHYA does not answer yes/no. It reasons through: what's actually new → patent eligibility → traditional-knowledge concerns → prior-art considerations → biodiversity/ABS considerations → relevant Indian law → international considerations → answer + evidence + sources.

## 3. Core modules (MVP scope)

| # | Module | Purpose |
|---|---|---|
| 1 | **AI IP & Regulatory Assistant** | Main chatbot; answers only from retrieved sources, never from general LLM knowledge alone |
| 2 | **Product/Formulation Analyzer** | Classifies product (classical medicine / proprietary / Ayurveda-Aahar / nutraceutical / phytopharma / cosmetic) as *preliminary AI-assisted classification*, never an official determination |
| 3 | **IP Recommendation Engine** | Surfaces relevant IP categories (patent, trademark, GI, design, copyright, trade secret, traditional knowledge/biodiversity) with relevance + reasoning |
| 4 | **Regulatory Checklist** | Generates a sourced, item-by-item compliance checklist instead of a wall of legal text |
| 5 | **Source-Cited RAG** | The heart of the system — every legal claim ships with a citation and an evidence-strength indicator |
| 6 | **India / International Mode** | Explicit jurisdiction toggle; answers never silently mix Indian and international law |
| 7 | **Multilingual AI** | MVP: English, Hindi, Telugu. Query is translated for understanding; retrieval and citation stay anchored to the authoritative-language source |
| 8 | **Human Escalation** | When confidence is low, the system says so and offers a path to human review — it never bluffs |

## 4. MVP scope lock

**In scope:**
- 3 languages: English, Hindi, Telugu
- 5–6 IP domains: Patent, Trademark, GI, Copyright, Design, Trade Secret
- Regulatory areas: AYUSH medicines, Ayurveda-Aahar, Biodiversity/ABS, cosmetics/phytopharmaceutical basics
- Sources: India Code, IP India, Ministry of AYUSH, FSSAI, WIPO, CBD/Nagoya-related material
- RAG over an existing LLM (Gemini/GPT) — no model training

**Explicitly out of scope for MVP:**
- Crawling the entire internet
- Training or fine-tuning a custom LLM
- 20-language voice assistant
- Every country's law
- A full Ayurveda product database
- A complex knowledge graph
- Fully automated legal-opinion generation
- Simultaneous mobile + web builds

## 5. UI shape (reference sketch)

**Home / input:**
- Jurisdiction toggle (🇮🇳 India / 🌍 International)
- Free-text "Describe your Ayurvedic product..." input
- Quick-action chips: Patent / Trademark / GI / Regulation / Biodiversity / Traditional Knowledge

**Result view:**
- Product Classification + confidence %
- IP Opportunities (🟢/🟡 relevance + why)
- Regulatory Considerations checklist (☑/☐, each item sourced)
- Evidence panel (Act, Section, source link, "View Source")

## 6. Success criteria for the hackathon demo

- A judge can ask a realistic question ("Can I patent my Ashwagandha-based formulation?") and get an answer with a real, correctly-cited section from an actual Act.
- The system visibly abstains or flags low confidence on at least one under-covered question — proving it doesn't fabricate.
- Jurisdiction toggle visibly changes which sources are used.
- At least one full flow works end-to-end in Hindi or Telugu.

## 7. Related documents
- `RULES.md` — hard development/safety rules the AI/dev team must follow
- `ARCHITECTURE.md` — data model, storage layers, RAG pipeline
- `AGENTS.md` — instructions for AI coding agents working in this repo
