"""
Product Analysis — Grounded LLM Prompt Construction.

Builds the system + user prompt for the ONE product analysis LLM call.
The LLM is asked to return a structured JSON object.

STRICT RULES encoded in the system prompt:
1. Answer ONLY from supplied evidence — never from training knowledge.
2. No fabricated statutes, sections, rules, citations, URLs, requirements.
3. Clearly use preliminary language: "may", "potentially", "subject to verification".
4. User-selected classification is PRELIMINARY — never state it is legally verified.
5. If evidence is insufficient for a dimension, state so explicitly in the field.
6. Do not give legal advice — provide decision-support information only.
7. Recommend professional/regulatory review.
8. Preserve citation_id values from evidence exactly (e.g. cit_abc123).
9. Only cite sources whose citation_id appears in the evidence block.
10. Jurisdiction is explicit — never mix Indian and international law.
11. Return ONLY valid JSON. No markdown, no explanation outside the JSON.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from src.features.product_analysis.domain.product_request import ProductAnalysisRequest

# JSON schema injected into the prompt for the LLM to follow exactly
_RESPONSE_SCHEMA = """{
  "grounded_summary": "<concise preliminary analysis summary — 1-2 paragraphs based strictly on evidence>",
  "classification": {
    "user_selected": "<user's stated hypothesis or 'No preference — let AYUSHYA assess'>",
    "preliminary_assessment": "<overall grounded classification narrative>",
    "evidence_strength": "<strong|moderate|weak|insufficient>",
    "requires_verification": true,
    "primary": {
      "category": "<e.g. Ayurveda-Aahara | Proprietary Ayurvedic Formulation | Ayurvedic Drug / Medicine | Phytopharmaceutical | Ayurvedic Cosmetic | Not Established>",
      "status": "<potentially_applicable|not_established|insufficient_evidence|requires_verification>",
      "evidence_strength": "<strong|moderate|weak|insufficient>",
      "requires_verification": true,
      "reasoning": "<evidence-grounded explanation of why this category may apply>"
    },
    "alternatives": [
      {
        "category": "<alternative category candidate>",
        "status": "<potentially_applicable|not_established|insufficient_evidence|requires_verification>",
        "evidence_strength": "<strong|moderate|weak|insufficient>",
        "reasoning": "<why this alternative framework must also be considered>"
      }
    ],
    "missing_information": [
      "<specific missing facts needed for definitive legal determination, e.g. exact classical reference text, manufacturing extraction ratio, or route of administration>"
    ],
    "decision_signals": {
      "product_form": "<e.g. Tablet form is relevant to dosage form & drug/food classification analysis.>",
      "intended_use": "<e.g. General wellness use provides one classification signal.>",
      "claims": "<e.g. Health vs disease claims influence regulatory domain boundary.>",
      "disease_claims": "<e.g. Disease treatment/prevention claims increase regulatory sensitivity under Drugs & Cosmetics Act Section 3 and Drugs & Magic Remedies Act.>",
      "classical_basis": "<e.g. Classical Ayurvedic reference availability dictates classical vs proprietary framework.>",
      "processing": "<e.g. Extract standardization influences phytopharmaceutical consideration.>",
      "ingredients": "<e.g. Botanical herbs trigger consideration of relevant AYUSH, food, and biodiversity frameworks.>"
    },
    "supporting_citation_ids": ["<cit_xxx>", ...]
  },
  "ip_assessment": [
    {
      "ip_type": "<Patent|Trademark|GI|Design|Trade Secret|Copyright>",
      "relevance": "<potentially_relevant|low_relevance|insufficient_evidence>",
      "preliminary_assessment": "<preliminary text>",
      "reasoning": "<evidence-based reasoning>",
      "evidence_strength": "<strong|moderate|weak|insufficient>",
      "requires_verification": true,
      "supporting_citation_ids": ["<cit_xxx>", ...]
    }
  ],
  "regulatory_assessment": [
    {
      "framework": "<name of regulatory framework>",
      "why_applicable": "<why it may apply>",
      "relevant_provisions": ["<provision from evidence>", ...],
      "evidence_strength": "<strong|moderate|weak|insufficient>",
      "requires_verification": true,
      "supporting_citation_ids": ["<cit_xxx>", ...]
    }
  ],
  "tk_biodiversity": {
    "tk_considerations": "<TK considerations from evidence, or 'Insufficient evidence'>",
    "biodiversity_considerations": "<BD/ABS considerations from evidence>",
    "abs_note": "<ABS note from evidence>",
    "evidence_strength": "<strong|moderate|weak|insufficient>",
    "requires_verification": true,
    "supporting_citation_ids": ["<cit_xxx>", ...],
    "insufficient": <true if no biodiversity evidence was available, else false>
  },
  "compliance_checklist": [
    {
      "action": "<actionable item>",
      "reason": "<reason from evidence>",
      "legal_area": "<legal area>",
      "priority": "<high|medium|low>",
      "requires_verification": true,
      "supporting_citation_id": "<cit_xxx or omit if none>"
    }
  ]
}"""


def build_product_evidence_block(evidence_items: List[Dict[str, Any]], max_text_len: int = 1500) -> str:
    """
    Format the evidence items (selected and capped to LLM limit) into
    a structured context block for the LLM.
    """
    if not evidence_items:
        return "No evidence available."

    lines: List[str] = []
    for i, ev in enumerate(evidence_items, 1):
        cit: Dict[str, Any] = ev.get("citation", {})
        text: str = ev.get("text", "").strip()
        if len(text) > max_text_len:
            text = text[:max_text_len] + "..."

        lines.append(f"--- EVIDENCE {i} ---")
        lines.append(f"citation_id: {cit.get('citation_id', '')}")
        lines.append(f"title: {cit.get('title', '')}")

        if cit.get("section"):
            lines.append(f"section: {cit['section']}")
        if cit.get("section_title"):
            lines.append(f"section_title: {cit['section_title']}")
        if cit.get("subsection"):
            lines.append(f"subsection: {cit['subsection']}")
        if cit.get("chapter"):
            lines.append(f"chapter: {cit['chapter']}")
        if cit.get("page_start") is not None:
            lines.append(f"page: {cit['page_start']}")
        if cit.get("jurisdiction"):
            lines.append(f"jurisdiction: {cit['jurisdiction']}")
        if cit.get("domain"):
            lines.append(f"domain: {cit['domain']}")
        if cit.get("authority"):
            lines.append(f"authority: {cit['authority']}")

        lines.append(f"text: {text}")
        lines.append("")

    return "\n".join(lines)


def _format_ingredients(request: ProductAnalysisRequest) -> str:
    if not request.ingredients:
        return "Not specified"
    parts = []
    for ing in request.ingredients:
        part = ing.name
        if ing.quantity:
            part += f": {ing.quantity}"
            if ing.unit:
                part += f" {ing.unit}"
        parts.append(part)
    return "; ".join(parts)


def build_product_analysis_prompt(
    request: ProductAnalysisRequest,
    evidence_block: str,
    domains_queried: List[str],
) -> Tuple[str, str]:
    """
    Construct the system + user prompt for the grounded product analysis LLM call.
    """
    domains_str = (
        ", ".join(domains_queried) if domains_queried else "multiple legal domains"
    )

    system_prompt = (
        "You are AYUSHYA, an AI regulatory and IP decision-support assistant for Ayurveda.\n"
        "Your role is to produce an independent, fact-driven, PRELIMINARY product formulation analysis "
        "based strictly on product facts and retrieved legal evidence.\n\n"
        "CLASSIFICATION PRINCIPLES — CRITICAL:\n"
        "1. DISTINGUISH USER HYPOTHESIS VS AYUSHYA ASSESSMENT: The user-selected classification is purely a user hypothesis ('user_selected'). "
        "Never automatically set AYUSHYA's preliminary classification to equal the user hypothesis.\n"
        "2. CONDITIONAL LEGAL REQUIREMENTS MUST NOT BE CONVERTED INTO UNCONDITIONAL OBLIGATIONS: Reason with preliminary and conditional language. "
        "PRELIMINARY LANGUAGE is mandatory ('may apply', 'potentially applicable', 'subject to verification'). Never claim official legal determination.\n"
        "3. FACT-DRIVEN REASONING: Product facts are signals, NOT definitive legal conclusions:\n"
        "   - Dosage form (e.g. tablet) does NOT automatically mean Ayurvedic Drug.\n"
        "   - Botanical ingredients (e.g. Ashwagandha) do NOT automatically mean Ayurveda-Aahar or Drug.\n"
        "   - Ayurvedic ingredient does NOT automatically mean Classical Formulation unless an exact classical reference is established.\n"
        "   - Standardized extract does NOT automatically mean Phytopharmaceutical.\n"
        "   - Disease claim does NOT automatically make the product a legally classified drug, but it increases regulatory sensitivity and triggers scrutiny under Drugs & Cosmetics Act Section 3 and Drugs & Magic Remedies Act.\n"
        "4. MULTI-CATEGORY AMBIGUITY: If product facts suggest overlapping frameworks (e.g. botanical tablet for wellness + disease claims or standardized extracts), return a primary category and list alternative categories in 'alternatives'. Do NOT force a single category if evidence is ambiguous.\n"
        "5. MISSING INFORMATION & UNCERTAINTY: If facts/evidence are missing or unverified (e.g. missing classical reference text, extraction ratios, or intended route), explicitly list them under 'missing_information', use status='potentially_applicable', 'insufficient_evidence', or 'not_established', and keep requires_verification=true.\n"
        "6. DECISION SIGNALS: Fill 'decision_signals' mapping product attributes (product_form, intended_use, claims, disease_claims, classical_basis, processing, ingredients) to their analytical significance grounded in evidence.\n"
        "7. STRICT GROUNDING & NO FABRICATION: Answer ONLY from the evidence supplied. Use ONLY citation_ids present in the evidence block (e.g. cit_xxx).\n"
        "8. JURISDICTION ISOLATION: Do NOT mix Indian law and international law in one claim.\n"
        "9. INTERNATIONAL JURISDICTION RULES: When Target Jurisdiction is International and destination country is unspecified:\n"
        "   - Do NOT invent destination country classifications (e.g. 'Botanical Dietary Supplement') unless backed by retrieved evidence for a specific country.\n"
        "   - Set primary category to 'Undetermined (Destination Target Country Not Specified)' with status='not_established'.\n"
        "   - Treat international treaties (CBD, Nagoya Protocol, TRIPS, PCT) strictly as international access/IP frameworks, NOT as destination country product regulations.\n"
        "   - Distinguish Indian biological resource origin export obligations (Biological Diversity Act 2002 / ABS Regulations) from destination country import/market authorization rules.\n"
        "   - Include 'Destination target country for import and market authorization' in missing_information.\n\n"
        f"Legal domains covered: {domains_str}.\n\n"
        "OUTPUT FORMAT — CRITICAL:\n"
        "Return ONLY a valid JSON object matching the schema below. No preamble, no markdown fences, no text outside JSON.\n\n"
        f"Schema:\n{_RESPONSE_SCHEMA}"
    )

    ingredient_str = _format_ingredients(request)
    disease_flag = getattr(request, "disease_claim_flag", False)
    disease_text = getattr(request, "disease_claim_text", "")
    disease_claim_info = (
        f"\nDisease Claim Flagged: YES — Claim Text: '{disease_text}'"
        if disease_flag or disease_text
        else "\nDisease Claim Flagged: No explicit disease claim indicated."
    )
    is_classical = getattr(request, "is_classical_basis", "unknown")
    classical_ref = getattr(request, "classical_reference", "")
    if is_classical == "unknown" or not classical_ref:
        classical_info = (
            "\nClassical Ayurvedic Basis: UNKNOWN / CLAIMED TRADITIONAL INSPIRATION — "
            "Authoritative classical formulation reference could not be independently established."
        )
    else:
        classical_info = (
            f"\nClassical Ayurvedic Basis: {is_classical.upper()} — Reference Source: {classical_ref}"
        )
    mfg_proc = getattr(request, "manufacturing_processing", "")
    processing_info = (
        f"\nManufacturing / Processing Details: {mfg_proc}"
        if mfg_proc
        else ""
    )
    claims = getattr(request, "product_claims", "")
    claims_info = (
        f"\nProduct Health Claims: {claims}"
        if claims
        else ""
    )
    intended_use = getattr(request, "intended_use", "")
    product_form = getattr(request, "product_form", getattr(request, "form", ""))

    user_prompt = (
        f"PRODUCT FORMULATION ANALYSIS REQUEST\n\n"
        f"Product Name: {request.product_name}\n"
        f"Product Form: {product_form}\n"
        f"Intended Use: {intended_use}\n"
        f"Proposed Classification Hypothesis (User Input): {request.user_selected_classification}"
        f"{claims_info}"
        f"{disease_claim_info}"
        f"{classical_info}"
        f"{processing_info}\n"
        f"Target Jurisdiction: {request.jurisdiction}\n"
        f"Ingredients: {ingredient_str}\n"
        f"Description & Notes: {request.description}\n\n"
        f"EVIDENCE (answer ONLY from this block — do not use knowledge outside this block):\n"
        f"{evidence_block}\n\n"
        "Complete the JSON object with all six top-level fields:\n"
        "grounded_summary, classification, ip_assessment, regulatory_assessment, tk_biodiversity, compliance_checklist.\n\n"
        "Return ONLY the JSON object. Start directly with '{' and end with '}'."
    )

    return system_prompt, user_prompt

