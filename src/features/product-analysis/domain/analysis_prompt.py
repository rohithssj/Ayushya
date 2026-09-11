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
  "grounded_summary": "<overall preliminary analysis narrative — 2-4 paragraphs>",
  "classification": {
    "user_selected": "<user's stated classification>",
    "preliminary_assessment": "<evidence-based preliminary note>",
    "evidence_strength": "<strong|moderate|weak|insufficient>",
    "requires_verification": true,
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


def build_product_evidence_block(evidence_items: List[Dict[str, Any]]) -> str:
    """
    Format the evidence items (selected and capped to LLM limit) into
    a structured context block for the LLM.

    Only includes fields that exist in actual chunk metadata.
    Does not fabricate any field value.
    """
    if not evidence_items:
        return "No evidence available."

    lines: List[str] = []
    for i, ev in enumerate(evidence_items, 1):
        cit: Dict[str, Any] = ev.get("citation", {})
        text: str = ev.get("text", "").strip()

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

    Returns: (system_prompt, user_prompt)

    The LLM is instructed to return ONLY a valid JSON object matching the schema.
    The parser (structured_response_parser.py) validates and sanitises the output.
    """
    domains_str = (
        ", ".join(domains_queried) if domains_queried else "multiple legal domains"
    )

    system_prompt = (
        "You are AYUSHYA, an AI regulatory and IP information assistant for Ayurveda. "
        "Your role is to produce a structured, grounded, PRELIMINARY product formulation "
        "analysis based ONLY on the retrieved statutory evidence provided.\n\n"
        "STRICT RULES — you MUST follow without exception:\n"
        "1. Answer ONLY from the evidence supplied. Do not use your training data, "
        "general knowledge of laws, or any information not present in the supplied evidence.\n"
        "2. NEVER invent, fabricate, or guess: laws, section numbers, regulation names, "
        "dates, authorities, URLs, page numbers, legal requirements, or compliance items.\n"
        "3. When citing a source, use ONLY the citation_id values from the supplied evidence "
        "(e.g. cit_abc123). Do not invent citation IDs. Do not cite a source not in the evidence.\n"
        "4. PRELIMINARY LANGUAGE is mandatory. Use: 'may apply', 'potentially applicable', "
        "'subject to verification', 'evidence indicates', 'preliminary assessment', "
        "'based on available evidence'. Never state definitive legal conclusions.\n"
        "5. The user-selected classification is PRELIMINARY USER INPUT — never treat it "
        "as a legally verified or officially determined classification.\n"
        "6. If the evidence does not cover a dimension (e.g. no biodiversity evidence "
        "was retrieved), state this explicitly in the relevant field and set "
        "evidence_strength to 'insufficient' and, for tk_biodiversity, 'insufficient' to true.\n"
        "7. This response is AI-assisted decision-support, NOT legal advice. "
        "Do not recommend specific legal strategies. Recommend consulting qualified "
        "IP attorneys, regulatory consultants, or AYUSH facilitators.\n"
        "8. Jurisdiction is explicit in each evidence item — NEVER mix Indian "
        "and international law in one claim.\n"
        "9. Do not fabricate compliance checklist items not supported by evidence.\n"
        "10. compliance_checklist must contain 3–7 items, each grounded in evidence.\n\n"
        f"Legal domains covered: {domains_str}.\n\n"
        "OUTPUT FORMAT — CRITICAL:\n"
        "Return ONLY a valid JSON object matching the schema below. "
        "Do NOT output any thinking process, reasoning, planning text, preamble, or scratchpad. "
        "Start directly with `{` and end with `}`. "
        "Keep text concise, factual, and direct to prevent truncation. "
        "No markdown code fences. No text before or after the JSON. "
        "No explanation. No apology. ONLY the JSON object.\n\n"
        f"Schema:\n{_RESPONSE_SCHEMA}"
    )

    ingredient_str = _format_ingredients(request)
    product_form = getattr(request, "product_form", getattr(request, "form", "Not specified"))
    traditional_knowledge_ref = getattr(request, "traditional_knowledge_ref", None)
    tk_ref = (
        f"\nTraditional/Classical Reference: {traditional_knowledge_ref}"
        if traditional_knowledge_ref
        else ""
    )

    user_prompt = (
        f"PRODUCT FORMULATION ANALYSIS REQUEST\n\n"
        f"Product Name: {request.product_name}\n"
        f"Product Form: {product_form}\n"
        f"User-Selected Target Classification (PRELIMINARY — not legally verified): "
        f"{request.user_selected_classification}\n"
        f"Target Jurisdiction: {request.jurisdiction}\n"
        f"Ingredients: {ingredient_str}\n"
        f"Description & Processing Method: {request.description}"
        f"{tk_ref}\n\n"
        f"EVIDENCE (answer ONLY from this block — do not use knowledge outside this block):\n"
        f"{evidence_block}\n\n"
        "Using ONLY the evidence above, complete the JSON object with all six fields:\n"
        "grounded_summary, classification, ip_assessment, regulatory_assessment, "
        "tk_biodiversity, compliance_checklist.\n\n"
        "Use only citation_ids from the evidence. If a field has no supporting evidence, "
        "set evidence_strength to 'insufficient' and explain in the text field.\n\n"
        "Return ONLY the JSON object. No markdown fences. No prose before or after."
    )

    return system_prompt, user_prompt
