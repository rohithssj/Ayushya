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

    Routing logic:
    1. Product classification — included for the user's selected product class.
    2. Patents + traditional knowledge — always included (patentability
       and TK exclusions are relevant to any novel formulation).
    3. Trademarks — always included (brand protection is relevant to any
       commercial product).
    4. Regulatory (AYUSH / drugs-cosmetics / ayurveda-aahar) — included
       based on the user-selected classification.
    5. Biodiversity / ABS — included if ingredients suggest use of Indian
       biological resources (keyword-based signal, not a legal determination).
    6. Copyright/design — included only when product attributes suggest packaging,
       label, artistic, visual, or appearance-protection questions.
    7. International treaties (CBD, TRIPS, Nagoya) — included only when
       jurisdiction = 'international'.
    8. GI — included if product references a traditional regional preparation.
    """

    def route(self, request: ProductAnalysisRequest) -> List[AnalysisDimension]:
        """
        Return the list of AnalysisDimensions relevant for this product.

        Dimensions are returned in logical analysis order:
        classification → regulatory → patents → trademarks → TK/biodiversity
        → international (if applicable).
        """
        dimensions: List[AnalysisDimension] = []

        cls_lower = request.user_selected_classification.lower()
        jur = request.jurisdiction.lower()
        desc_lower = request.description.lower()
        form_lower = request.product_form.lower()
        product_name_lower = request.product_name.lower()

        # ── 1. Product classification (target user's selected class) ───────
        if any(k in cls_lower for k in ("aahar", "food", "nutraceutical", "dietary")):
            dimensions.append(
                AnalysisDimension(
                    dimension="product_classification",
                    legal_domain="ayurveda-aahar",
                    why_relevant=(
                        "The user's selected classification references Ayurveda-Aahar, "
                        "food, nutraceutical, or dietary-product concepts."
                    ),
                )
            )
        elif any(
            k in cls_lower
            for k in ("proprietary", "classical", "asu", "medicine", "phyto", "cosmetic")
        ) or "cream" in form_lower or "oil" in form_lower:
            dimensions.append(
                AnalysisDimension(
                    dimension="product_classification",
                    legal_domain="drugs-cosmetics",
                    why_relevant=(
                        "The user's selected classification or product form references "
                        "medicine, ASU, phytopharmaceutical, or cosmetic concepts."
                    ),
                )
            )

        # ── 2. Patent IP (always) ──────────────────────────────────────────
        dimensions.append(
            AnalysisDimension(
                dimension="patent_ip",
                legal_domain="patents",
                why_relevant=(
                    "Patent eligibility and non-patentable subject matter provisions "
                    "are relevant to any novel Ayurvedic formulation, particularly "
                    "regarding traditional knowledge exclusions."
                ),
            )
        )

        # ── 3. Regulatory — AYUSH / Drugs & Cosmetics ─────────────────────
        if any(
            k in cls_lower
            for k in ("proprietary", "classical", "asu", "medicine", "phyto")
        ):
            dimensions.append(
                AnalysisDimension(
                    dimension="regulatory_drugs_cosmetics",
                    legal_domain="drugs-cosmetics",
                    why_relevant=(
                        "Product classification as a medicine or phytopharmaceutical "
                        "may engage the Drugs and Cosmetics Act regulatory framework."
                    ),
                )
            )
        elif "cosmetic" in cls_lower or "cream" in form_lower or "oil" in form_lower:
            dimensions.append(
                AnalysisDimension(
                    dimension="regulatory_drugs_cosmetics",
                    legal_domain="drugs-cosmetics",
                    why_relevant=(
                        "A cosmetic or topical product form may engage the Drugs and "
                        "Cosmetics Act (Schedule S / Cosmetics Rules) framework."
                    ),
                )
            )

        # ── 4. Regulatory — Ayurveda-Aahar / FSSAI ────────────────────────
        if any(k in cls_lower for k in ("aahar", "food", "nutraceutical", "dietary")):
            dimensions.append(
                AnalysisDimension(
                    dimension="regulatory_ayurveda_aahar",
                    legal_domain="ayurveda-aahar",
                    why_relevant=(
                        "A product classified as Ayurveda-Aahar or a food supplement "
                        "may be subject to FSSAI Ayurveda Aahar regulations."
                    ),
                )
            )
        # Also add if not already captured and classification is ambiguous
        if not any(d.legal_domain == "ayurveda-aahar" for d in dimensions) and not any(
            d.legal_domain == "drugs-cosmetics" for d in dimensions
        ):
            dimensions.append(
                AnalysisDimension(
                    dimension="regulatory_ayurveda_aahar",
                    legal_domain="ayurveda-aahar",
                    why_relevant=(
                        "Ayurveda-Aahar regulatory framework may apply depending on "
                        "how the product is marketed and whether it relies on "
                        "authoritative Ayurvedic text references."
                    ),
                )
            )

        # ── 5. Traditional Knowledge / Biodiversity ────────────────────────
        ingredient_text = " ".join(
            ing.name.lower() for ing in request.ingredients
        )
        combined_text = ingredient_text + " " + desc_lower

        has_botanical_signal = any(
            signal in combined_text for signal in _INDIAN_BOTANICAL_SIGNALS
        )

        if has_botanical_signal or "traditional" in desc_lower or "classical" in desc_lower:
            dimensions.append(
                AnalysisDimension(
                    dimension="traditional_knowledge",
                    legal_domain="biodiversity",
                    why_relevant=(
                        "One or more ingredients appear to be Indian biological resources "
                        "or the description references traditional processing. Biodiversity "
                        "Act and Access and Benefit Sharing (ABS) considerations may apply."
                    ),
                )
            )

        # ── 6. Trademark ──────────────────────────────────────────────────
        dimensions.append(
            AnalysisDimension(
                dimension="trademark",
                legal_domain="trademarks",
                why_relevant=(
                    "Trademark registration may be available for the product or brand name "
                    "if it is distinctive and not purely descriptive."
                ),
            )
        )

        # ── 7. Design / Copyright (conditional product presentation signals) ─
        visual_text = " ".join((product_name_lower, desc_lower, form_lower))
        design_signals = frozenset(
            {
                "packaging", "bottle", "container", "shape", "ornamental",
                "visual design", "appearance", "label design", "trade dress",
            }
        )
        if any(sig in visual_text for sig in design_signals):
            dimensions.append(
                AnalysisDimension(
                    dimension="design_protection",
                    legal_domain="designs",
                    why_relevant=(
                        "The product description references packaging, shape, "
                        "appearance, or visual-design attributes."
                    ),
                )
            )

        copyright_signals = frozenset(
            {
                "label", "brochure", "leaflet", "manual", "logo artwork",
                "artwork", "literary", "website copy", "marketing copy",
            }
        )
        if any(sig in visual_text for sig in copyright_signals):
            dimensions.append(
                AnalysisDimension(
                    dimension="copyright_material",
                    legal_domain="copyright",
                    why_relevant=(
                        "The product description references label, artwork, "
                        "literary, or marketing material."
                    ),
                )
            )

        # ── 8. GI (Geographical Indication) ──────────────────────────────
        # Include if description mentions region-specific preparations
        gi_signals = frozenset(
            {"kashmir", "kerala", "rajasthan", "assam", "darjeeling", "banaras",
             "mysore", "kangra", "araku", "coorg", "nilgiri", "regional", "geographical"}
        )
        if any(sig in combined_text for sig in gi_signals):
            dimensions.append(
                AnalysisDimension(
                    dimension="gi_protection",
                    legal_domain="gi",
                    why_relevant=(
                        "The product description or ingredients may have geographical "
                        "significance that could engage Geographical Indication protections."
                    ),
                )
            )

        # ── 9. International treaties ─────────────────────────────────────
        if jur == "international":
            dimensions.append(
                AnalysisDimension(
                    dimension="international_treaties",
                    legal_domain="treaties",
                    why_relevant=(
                        "International jurisdiction was selected. CBD, Nagoya Protocol, "
                        "TRIPS, and PCT considerations may apply for international "
                        "IP protection or ABS obligations."
                    ),
                )
            )
            # Also add CBD specifically for biodiversity dimension if not already present
            if not any(d.legal_domain == "cbd" for d in dimensions):
                dimensions.append(
                    AnalysisDimension(
                        dimension="cbd_nagoya",
                        legal_domain="cbd",
                        why_relevant=(
                            "The Convention on Biological Diversity (CBD) and Nagoya Protocol "
                            "may be relevant for international commercialisation of "
                            "products using Indian biological resources."
                        ),
                    )
                )

        return dimensions
