"""
Product Analysis — Targeted Query Builder.

Constructs focused retrieval queries per analysis dimension.

DESIGN RULES:
- Queries are designed to RETRIEVE evidence, not to decide the law.
- No hardcoded legal conclusions are encoded into query text.
- Queries are constructed from product attributes only.
- Queries must be specific enough to surface relevant corpus chunks
  without being so narrow that they miss adjacent provisions.
- Each query targets one AnalysisDimension.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from src.features.product_analysis.domain.product_request import ProductAnalysisRequest
from src.features.product_analysis.domain.domain_router import AnalysisDimension


# ---------------------------------------------------------------------------
# TargetedQuery model
# ---------------------------------------------------------------------------


@dataclass
class TargetedQuery:
    """
    A single focused retrieval query for one analysis dimension.

    query_text:  the actual query string sent to HybridRetrievalUseCase
    dimension:   the analysis dimension this query serves
    legal_domain: the corpus domain filter for this query
    jurisdiction: the jurisdiction filter for this query
    why_constructed: non-legal explanation of why this query was built
    """

    query_text: str
    dimension: str
    legal_domain: str
    jurisdiction: str
    why_constructed: str


# ---------------------------------------------------------------------------
# Query Builder
# ---------------------------------------------------------------------------


class QueryBuilder:
    """
    Builds a list of TargetedQuery objects from a ProductAnalysisRequest
    and the list of AnalysisDimensions produced by DomainRouter.

    Each dimension gets exactly one query. Queries are parameterised from
    product attributes — ingredient names, form, classification — but never
    encode legal conclusions.
    """

    def build_queries(
        self,
        request: ProductAnalysisRequest,
        dimensions: List[AnalysisDimension],
    ) -> List[TargetedQuery]:
        """
        Return one TargetedQuery per AnalysisDimension.
        """
        queries: List[TargetedQuery] = []
        for dimension in dimensions:
            query = self._build_query_for_dimension(request, dimension)
            if query:
                queries.append(query)
        return queries

    # ── Private builders ──────────────────────────────────────────────────

    def _build_query_for_dimension(
        self,
        request: ProductAnalysisRequest,
        dimension: AnalysisDimension,
    ) -> Optional[TargetedQuery]:
        """Dispatch to the appropriate query builder by dimension."""
        dispatch = {
            "product_classification": self._build_classification_query,
            "patent_ip": self._build_patent_query,
            "regulatory_drugs_cosmetics": self._build_regulatory_dc_query,
            "regulatory_ayurveda_aahar": self._build_regulatory_aahar_query,
            "traditional_knowledge": self._build_tk_biodiversity_query,
            "trademark": self._build_trademark_query,
            "gi_protection": self._build_gi_query,
            "design_protection": self._build_design_query,
            "copyright_material": self._build_copyright_query,
            "international_treaties": self._build_international_query,
            "cbd_nagoya": self._build_cbd_query,
        }
        builder = dispatch.get(dimension.dimension)
        if builder:
            return builder(request, dimension)
        # For unknown dimensions, build a generic targeted query
        return self._build_generic_query(request, dimension)

    def _ingredient_summary(self, request: ProductAnalysisRequest, max_n: int = 5) -> str:
        """Produce a brief ingredient name string (first max_n names)."""
        names = [ing.name for ing in request.ingredients[:max_n]]
        return ", ".join(names) if names else ""

    def _product_context(self, request: ProductAnalysisRequest) -> str:
        """Compact product context for retrieval queries; no legal conclusions."""
        ing_str = self._ingredient_summary(request)
        parts = [
            request.product_name,
            request.product_form,
            request.user_selected_classification,
        ]
        if ing_str:
            parts.append(f"ingredients {ing_str}")
        if request.description:
            parts.append(request.description[:400])
        return " ".join(part for part in parts if part)

    def _build_classification_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        context = self._product_context(request)
        if dimension.legal_domain == "drugs-cosmetics":
            base = (
                "Ayurvedic Siddha Unani ASU medicine proprietary medicine classical "
                "formulation phytopharmaceutical cosmetic product classification definition"
            )
        else:
            base = (
                "Ayurveda Aahar food supplement nutraceutical dietary supplement "
                "product classification definition FSSAI"
            )

        return TargetedQuery(
            query_text=f"{base} {context}",
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets definitions and classification provisions relevant to the "
                "user-selected product category."
            ),
        )

    def _build_patent_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        ing_str = self._ingredient_summary(request)
        parts = [
            f"patent eligibility non-patentable subject matter traditional knowledge exclusions",
            f"Section 3 patentable inventions",
        ]
        if ing_str:
            parts.append(f"formulation containing {ing_str}")
        if "traditional" in request.description.lower() or "classical" in request.description.lower():
            parts.append("traditional knowledge prior art TKDL Section 3(p) aggregation admixture")
        if "extract" in request.description.lower() or "standardized" in request.description.lower():
            parts.append("novel extraction process synergistic formulation inventive step")

        return TargetedQuery(
            query_text=" ".join(parts),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets patent eligibility provisions, TK exclusions under Section 3(p)/3(e), "
                "and inventive step requirements relevant to this formulation."
            ),
        )

    def _build_regulatory_dc_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        ing_str = self._ingredient_summary(request)
        form_str = request.product_form

        return TargetedQuery(
            query_text=(
                f"Drugs Cosmetics Act Rules manufacturing license AYUSH proprietary medicine "
                f"Schedule E prohibited substances labeling requirements "
                f"{form_str} formulation"
                + (f" containing {ing_str}" if ing_str else "")
            ),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets Drugs and Cosmetics Act/Rules provisions potentially applicable "
                "to this product form and classification."
            ),
        )

    def _build_regulatory_aahar_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        ing_str = self._ingredient_summary(request)

        return TargetedQuery(
            query_text=(
                "Ayurveda Aahar FSSAI regulations food supplement dietary supplement "
                "Schedule A authoritative texts labeling packaging requirements "
                "registration approval"
                + (f" {ing_str}" if ing_str else "")
            ),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets FSSAI Ayurveda Aahar regulatory requirements applicable "
                "to Ayurvedic food supplements."
            ),
        )

    def _build_tk_biodiversity_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        ing_str = self._ingredient_summary(request, max_n=3)

        return TargetedQuery(
            query_text=(
                "Biological Diversity Act biological resources access benefit sharing "
                "National Biodiversity Authority NBA prior approval ABS "
                "traditional knowledge TKDL"
                + (f" {ing_str}" if ing_str else "")
            ),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets Biological Diversity Act provisions and ABS requirements "
                "potentially applicable when using Indian biological resources."
            ),
        )

    def _build_trademark_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        return TargetedQuery(
            query_text=(
                "Trade Marks Act trademark registration classes descriptive marks "
                "pharmaceutical herbal wellness product class 5 Class 30 "
                "distinctive brand name registration requirements"
            ),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets Trade Marks Act provisions relevant to registering a brand "
                "name for a health/wellness product."
            ),
        )

    def _build_gi_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        return TargetedQuery(
            query_text=(
                "Geographical Indications of Goods Registration Protection Act "
                "GI registration traditional product regional origin "
                "Ayurvedic traditional preparation geographical indication"
            ),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets GI Act provisions relevant to products with potential "
                "geographical or traditional regional significance."
            ),
        )

    def _build_design_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        return TargetedQuery(
            query_text=(
                "Designs Act product design registration shape configuration pattern "
                "ornament composition of lines packaging appearance "
                f"{self._product_context(request)}"
            ),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets design-protection provisions only because the product "
                "description contains visual or appearance-related signals."
            ),
        )

    def _build_copyright_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        return TargetedQuery(
            query_text=(
                "Copyright Act artistic work literary work label artwork brochure "
                "marketing material packaging copy protection "
                f"{self._product_context(request)}"
            ),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets copyright provisions only because the product description "
                "contains label, artwork, literary, or marketing-material signals."
            ),
        )

    def _build_international_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        ing_str = self._ingredient_summary(request, max_n=3)

        return TargetedQuery(
            query_text=(
                "TRIPS Agreement patent protection traditional knowledge CBD Nagoya Protocol "
                "PCT international patent application prior art "
                "Access and Benefit Sharing international obligations"
                + (f" {ing_str}" if ing_str else "")
            ),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets TRIPS, CBD, Nagoya Protocol, and PCT provisions relevant "
                "for international IP protection of an Ayurvedic formulation."
            ),
        )

    def _build_cbd_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        return TargetedQuery(
            query_text=(
                "Convention on Biological Diversity CBD Nagoya Protocol access "
                "benefit sharing mutually agreed terms provider country "
                "biological resources genetic resources traditional knowledge"
            ),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=(
                "Targets CBD/Nagoya Protocol provisions for international ABS obligations."
            ),
        )

    def _build_generic_query(
        self, request: ProductAnalysisRequest, dimension: AnalysisDimension
    ) -> TargetedQuery:
        ing_str = self._ingredient_summary(request)
        return TargetedQuery(
            query_text=(
                f"{dimension.dimension.replace('_', ' ')} legal requirements "
                f"{request.product_form} Ayurvedic formulation"
                + (f" containing {ing_str}" if ing_str else "")
            ),
            dimension=dimension.dimension,
            legal_domain=dimension.legal_domain,
            jurisdiction=request.jurisdiction,
            why_constructed=f"Generic query for dimension: {dimension.dimension}.",
        )
