"""
Product Analysis — Domain Router.

Determines which legal analysis dimensions (and their corresponding
legal domain filters) are relevant for a given product formulation.

DESIGN RULES:
- The router determines WHICH domains to query — it does NOT decide the law.
- No legal conclusions are encoded here.
- Routing is transparent, rule-based, and deterministic.
- Every routing decision is based only on product attributes supplied by the user.
- Routing adds retrieval dimensions; it does not pre-determine outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from src.features.product_analysis.domain.product_request import ProductAnalysisRequest


# ---------------------------------------------------------------------------
# Analysis Dimension
# ---------------------------------------------------------------------------


@dataclass
class AnalysisDimension:
    """
    One targeted analysis dimension for a product formulation.

    dimension:    human-readable label (e.g. 'patent_ip', 'regulatory_ayush')
    legal_domain: the corpus domain filter to use for retrieval
                  (must match VALID_DOMAINS in retrieval_api.ts)
    why_relevant: non-legal reason this dimension was selected
                  (based solely on product attributes — not a legal conclusion)
    """

    dimension: str
    legal_domain: str
    why_relevant: str


# ---------------------------------------------------------------------------
# Domain Router
# ---------------------------------------------------------------------------

# Ingredient keywords that suggest Indian biological resources may be involved.
# This triggers biodiversity/ABS dimension routing — not a legal determination.
_INDIAN_BOTANICAL_SIGNALS = frozenset(
    {
        "ashwagandha", "withania", "somnifera",
        "pippali", "piper longum", "long pepper",
        "brahmi", "bacopa",
        "neem", "azadirachta",
        "tulsi", "ocimum",
        "turmeric", "curcuma",
        "shatavari", "asparagus racemosus",
        "guduchi", "tinospora",
        "amla", "phyllanthus emblica", "emblica officinalis",
        "triphala",
        "haritaki", "terminalia chebula",
        "bibhitaki", "terminalia bellirica",
        "arjuna", "terminalia arjuna",
        "giloy",
        "mulethi", "glycyrrhiza",
        "shankhpushpi", "convolvulus",
        "vacha", "acorus calamus",
        "gokshura", "tribulus",
        "moringa",
        "karela", "momordica",
        "garcinia",
        "boswellia", "shallaki",
        "punarnava", "boerhavia",
        "vidanga", "embelia",
        "bala", "sida cordifolia",
        "manjistha", "rubia cordifolia",
        "sariva", "hemidesmus",
    }
)


class DomainRouter:
    """
    Routes a ProductAnalysisRequest to the set of AnalysisDimensions
    that should be queried for a complete multi-domain analysis.

    Fact-Driven Routing Logic (Independent of User Hypothesis):
    1. Product Classification & Regulatory Frameworks:
       - Evaluates intended_use, product_claims, disease_claim_flag, product_form, classical basis, processing.
       - Disease claims ("treat", "cure", "prevent", "mitigate", "diabetes", etc.) or disease_claim_flag=True:
         always routes to 'drugs-cosmetics' (Drugs and Cosmetics Act + Magic Remedies Act) for claim sensitivity evaluation.
       - Oral botanical wellness / dietary supplements: routes to both 'ayurveda-aahar' AND 'drugs-cosmetics'
         to evaluate potential overlap / boundary rules.
       - Topical / Cosmetic forms (cream, cosmetic oil, skin/hair care intended use): routes to 'drugs-cosmetics' (Cosmetics Rules).
       - User hypothesis (if not 'no_preference'): added as an extra verification target, NEVER restricting fact-driven routing.
    2. Patents + Traditional Knowledge: always included (Section 3 exclusions, TKDL, inventive step).
    3. Compliance Checklist: routes across applicable regulatory domains.
    4. Biodiversity / ABS: triggered by botanical ingredients or classical processing context.
    5. Trademarks, GI, Designs, Copyright, International Treaties as applicable.
    """

    def route(self, request: ProductAnalysisRequest) -> List[AnalysisDimension]:
        dimensions: List[AnalysisDimension] = []

        cls_lower = (request.user_selected_classification or "").lower()
        jur = request.jurisdiction.lower()
        desc_lower = (request.description or "").lower()
        intended_lower = (request.intended_use or "").lower()
        claims_lower = (request.product_claims or "").lower()
        disease_text_lower = (request.disease_claim_text or "").lower()
        form_lower = (request.product_form or "").lower()
        product_name_lower = (request.product_name or "").lower()

        combined_context = " ".join([
            desc_lower, intended_lower, claims_lower, disease_text_lower, product_name_lower
        ])

        # ── Disease Claim Detection Signal ─────────────────────────────
        disease_keywords = (
            "treat", "cure", "prevent", "mitigate", "diabetes", "arthritis",
            "cancer", "disease", "disorder", "infection", "therapeutic", "healing",
            "remedy", "hypertension", "ulcer", "asthma"
        )
        has_disease_claim = (
            request.disease_claim_flag or
            any(k in combined_context for k in disease_keywords)
        )

        # ── 1. Fact-Driven Classification & Regulatory Domain Routing ───

        # Food / Ayurveda-Aahar Signal: wellness, dietary, food, immunity, stress support, oral supplement
        has_aahar_signal = (
            any(k in combined_context for k in ("wellness", "immune", "immunity", "stress", "digestion", "food", "aahar", "dietary", "supplement", "general health")) or
            any(k in cls_lower for k in ("aahar", "food", "nutraceutical", "dietary")) or
            cls_lower in ("no_preference", "no preference — let ayushya assess")
        )

        # Drug / ASU Medicine Signal: disease claims, therapeutic intent, drug keywords, or dosage form (tablet/capsule)
        has_drug_signal = (
            has_disease_claim or
            any(k in form_lower for k in ("tablet", "capsule", "pill", "syrup", "injection")) or
            any(k in combined_context for k in ("medicine", "asu", "drug", "phytopharmaceutical", "therapeutic")) or
            any(k in cls_lower for k in ("drug", "medicine", "proprietary", "phytopharmaceutical"))
        )

        # Cosmetic Signal: topical form (cream, oil), cosmetic intended use (skin, hair, beauty, cleansing)
        has_cosmetic_signal = (
            any(k in form_lower for k in ("cream", "lotion", "gel", "paste")) or
            any(k in combined_context for k in ("skin", "hair", "beauty", "cosmetic", "cleansing", "topical")) or
            "cosmetic" in cls_lower
        )

        # Route to Ayurveda-Aahar domain if food/supplement/wellness signals exist or unconstrained
        if has_aahar_signal or (not has_cosmetic_signal and not has_disease_claim):
            dimensions.append(
                AnalysisDimension(
                    dimension="product_classification",
                    legal_domain="ayurveda-aahar",
                    why_relevant=(
                        "Product intended use, wellness claims, or formulation facts trigger consideration "
                        "of the Ayurveda-Aahar regulatory framework (FSSAI Regulations, 2022)."
                    ),
                )
            )

        # Route to Drugs & Cosmetics domain if drug signals, disease claims, ASU, or cosmetic signals exist
        if has_drug_signal or has_cosmetic_signal or has_disease_claim or cls_lower in ("no_preference", "no preference — let ayushya assess"):
            dimensions.append(
                AnalysisDimension(
                    dimension="regulatory_drugs_cosmetics",
                    legal_domain="drugs-cosmetics",
                    why_relevant=(
                        "Product attributes (disease/health claims, dosage form, classical/proprietary context, "
                        "or cosmetic intended use) trigger evaluation under the Drugs and Cosmetics Act, 1940 "
                        "and Drugs and Magic Remedies Act, 1954."
                    ),
                )
            )

        # If user specified a specific proposed classification (hypothesis), add user hypothesis verification target
        if cls_lower and cls_lower not in ("no_preference", "no preference — let ayushya assess", "other", "other / not sure"):
            target_domain = "ayurveda-aahar" if any(k in cls_lower for k in ("aahar", "food", "nutraceutical")) else "drugs-cosmetics"
            if not any(d.legal_domain == target_domain for d in dimensions):
                dimensions.append(
                    AnalysisDimension(
                        dimension="user_proposed_verification",
                        legal_domain=target_domain,
                        why_relevant=f"User proposed target classification hypothesis '{request.user_selected_classification}' for verification.",
                    )
                )

        # ── 2. Patent IP (always included) ──────────────────────────────
        dimensions.append(
            AnalysisDimension(
                dimension="patent_ip",
                legal_domain="patents",
                why_relevant=(
                    "Patentability criteria (Section 3(p) traditional knowledge exclusions, "
                    "Section 3(e) mere admixture rules, Section 3(d) efficacy/new form rules, "
                    "and inventive step) are relevant to any Ayurvedic product formulation."
                ),
            )
        )

        # ── 3. Compliance Checklist ─────────────────────────────────────
        compliance_domain = "drugs-cosmetics" if has_disease_claim or has_drug_signal else "ayurveda-aahar"
        dimensions.append(
            AnalysisDimension(
                dimension="compliance_checklist",
                legal_domain=compliance_domain,
                why_relevant=(
                    "Statutory compliance obligations (labeling, claims, Schedule requirements, "
                    "licensing, and approval pathways) apply to this formulation."
                ),
            )
        )

        # ── 4. Traditional Knowledge / Biodiversity / ABS ──────────────
        ingredient_text = " ".join(ing.name.lower() for ing in request.ingredients)
        combined_ing_text = ingredient_text + " " + combined_context

        has_botanical_signal = any(
            signal in combined_ing_text for signal in _INDIAN_BOTANICAL_SIGNALS
        )

        if has_botanical_signal or request.is_classical_basis == "yes" or "traditional" in combined_context or "classical" in combined_context:
            dimensions.append(
                AnalysisDimension(
                    dimension="traditional_knowledge",
                    legal_domain="biodiversity",
                    why_relevant=(
                        "One or more botanical ingredients appear to be Indian biological resources "
                        "or the formulation references classical/traditional knowledge. Biological Diversity Act "
                        "and Access and Benefit Sharing (ABS) considerations apply."
                    ),
                )
            )

        # ── 5. Trademark (always included) ──────────────────────────────
        dimensions.append(
            AnalysisDimension(
                dimension="trademark",
                legal_domain="trademarks",
                why_relevant=(
                    "Trademark registration may be available for the product name/brand "
                    "if distinctive and not descriptive."
                ),
            )
        )

        # ── 6. Design / Copyright ──────────────────────────────────────
        visual_text = " ".join((product_name_lower, combined_context, form_lower))
        design_signals = frozenset(
            {"packaging", "bottle", "container", "shape", "ornamental", "visual design", "appearance", "label design", "trade dress"}
        )
        if any(sig in visual_text for sig in design_signals):
            dimensions.append(
                AnalysisDimension(
                    dimension="design_protection",
                    legal_domain="designs",
                    why_relevant="Product description references packaging, shape, or visual design attributes.",
                )
            )

        copyright_signals = frozenset(
            {"label", "brochure", "leaflet", "manual", "logo artwork", "artwork", "literary", "website copy", "marketing copy"}
        )
        if any(sig in visual_text for sig in copyright_signals):
            dimensions.append(
                AnalysisDimension(
                    dimension="copyright_material",
                    legal_domain="copyright",
                    why_relevant="Product description references label artwork, literary material, or marketing copy.",
                )
            )

        # ── 7. Geographical Indication (GI) ────────────────────────────
        gi_signals = frozenset(
            {"kashmir", "kerala", "rajasthan", "assam", "darjeeling", "banaras", "mysore", "kangra", "araku", "coorg", "nilgiri", "regional", "geographical"}
        )
        if any(sig in combined_ing_text for sig in gi_signals):
            dimensions.append(
                AnalysisDimension(
                    dimension="gi_protection",
                    legal_domain="gi",
                    why_relevant="Product attributes or ingredients mention regional or geographical indications.",
                )
            )

        # ── 8. International Treaties ──────────────────────────────────
        if jur == "international":
            dimensions.append(
                AnalysisDimension(
                    dimension="international_treaties",
                    legal_domain="treaties",
                    why_relevant=(
                        "International jurisdiction was selected. CBD, Nagoya Protocol, TRIPS, "
                        "and PCT considerations apply."
                    ),
                )
            )
            if not any(d.legal_domain == "cbd" for d in dimensions):
                dimensions.append(
                    AnalysisDimension(
                        dimension="cbd_nagoya",
                        legal_domain="cbd",
                        why_relevant="Convention on Biological Diversity (CBD) & Nagoya Protocol ABS considerations apply.",
                    )
                )

        return dimensions

