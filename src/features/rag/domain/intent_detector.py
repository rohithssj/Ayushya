"""
Phase 4 — Domain & Intent Detector for RAG Retrieval.

Lightweight, deterministic domain/intent classifier for retrieval query expansion
and domain relevance gating.

Supports:
- Domains: 'patents', 'trademarks', 'geographical_indications', 'copyright', 'designs', 'biodiversity', 'regulatory', 'general'
- Intent types: 'patentability', 'patent_procedure', 'trademark_registration', 'gi_protection', 'copyright_protection', 'abs_compliance', 'regulatory_compliance', 'general_query'

Supports English, Devanagari (Hindi), Telugu, Romanized Hindi, and Romanized Telugu queries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass
class IntentResult:
    domain: str
    intent_type: str
    confidence: float
    key_concepts: List[str]
    suggested_domain_filter: Optional[str] = None


_PATENT_PATTERNS = re.compile(
    r"(?:\b(?:patent|patents|patentability|patentable|inventive|novelty|prior art|section 3\(p\)|section 3\(d\)|tkdl|ayush guidelines|peetent|paitent)\b|పేటెంట్|पेटेंट)",
    re.IGNORECASE,
)

_TRADEMARK_PATTERNS = re.compile(
    r"(?:\b(?:trademark|trademarks|brand name|trade mark|logo|mark registration)\b|ट्रेडमार्क|ట్రేడ్‌మార్క్|ట్రేడ్ మార్క్)",
    re.IGNORECASE,
)

_GI_PATTERNS = re.compile(
    r"(?:\b(?:geographical indication|gi act|gi tag|gi registration|section 47)\b|भौगोलिक उपदर्शन|భౌగోళిక సూచిక)",
    re.IGNORECASE,
)

_COPYRIGHT_PATTERNS = re.compile(
    r"(?:\b(?:copyright|author rights|literary work|artistic work)\b|कॉपीराइट|కాపీరైట్)",
    re.IGNORECASE,
)

_BIODIVERSITY_PATTERNS = re.compile(
    r"(?:\b(?:biodiversity|biological diversity|abs|access and benefit sharing|nba|national biodiversity authority|state biodiversity board|biological resource|nagoya|cbd)\b|जैविक विविधता|జీవ వైవిధ్యం)",
    re.IGNORECASE,
)

_REGULATORY_PATTERNS = re.compile(
    r"(?:\b(?:fssai|ayurveda aahara|ayurveda-aahara|drugs and cosmetics|drugs and magic remedies|manufacturing license|licensing|shelf life|labelling)\b|खाद्य सुरक्षा|మందుల చట్టం)",
    re.IGNORECASE,
)



class IntentDetector:
    """Lightweight deterministic intent routing for RAG retrieval."""

    @staticmethod
    def detect_intent(query: str, normalized_query: Optional[str] = None) -> IntentResult:
        if not query or not query.strip():
            return IntentResult(
                domain="general",
                intent_type="general_query",
                confidence=1.0,
                key_concepts=[],
            )

        combined_text = f"{query} {normalized_query or ''}".strip()

        # 1. Patent Intent Match
        if _PATENT_PATTERNS.search(combined_text):
            concepts = ["patentability", "novelty", "inventive step", "Section 3(p)", "Patents Act 1970", "AYUSH examination guidelines"]
            intent_type = "patentability" if any(w in combined_text.lower() for w in ["patentability", "patentable", "protection", "receive", "get", "eligible", "loni", "ravali", "milega", "vastunda"]) else "patent_procedure"
            return IntentResult(
                domain="patents",
                intent_type=intent_type,
                confidence=0.95,
                key_concepts=concepts,
                suggested_domain_filter="patents",
            )

        # 2. Trademark Intent Match
        if _TRADEMARK_PATTERNS.search(combined_text):
            return IntentResult(
                domain="trademarks",
                intent_type="trademark_registration",
                confidence=0.95,
                key_concepts=["trademark registration", "Trade Marks Act 1999"],
                suggested_domain_filter="trademarks",
            )

        # 3. Geographical Indication Match
        if _GI_PATTERNS.search(combined_text):
            return IntentResult(
                domain="geographical_indications",
                intent_type="gi_protection",
                confidence=0.95,
                key_concepts=["Geographical Indications of Goods Act 1999"],
                suggested_domain_filter="geographical_indications",
            )

        # 4. Copyright Match
        if _COPYRIGHT_PATTERNS.search(combined_text):
            return IntentResult(
                domain="copyright",
                intent_type="copyright_protection",
                confidence=0.95,
                key_concepts=["Copyright Act 1957"],
                suggested_domain_filter="copyright",
            )

        # 5. Biodiversity / ABS Match
        if _BIODIVERSITY_PATTERNS.search(combined_text):
            return IntentResult(
                domain="biodiversity",
                intent_type="abs_compliance",
                confidence=0.95,
                key_concepts=["Biological Diversity Act 2002", "Access and Benefit Sharing"],
                suggested_domain_filter="biodiversity",
            )

        # 6. Regulatory Match
        if _REGULATORY_PATTERNS.search(combined_text):
            return IntentResult(
                domain="regulatory",
                intent_type="regulatory_compliance",
                confidence=0.95,
                key_concepts=["Drugs and Cosmetics Act", "FSSAI Ayurveda Aahara"],
                suggested_domain_filter="regulatory",
            )

        # Safe Fallback for unclassified queries
        return IntentResult(
            domain="general",
            intent_type="general_query",
            confidence=0.50,
            key_concepts=[],
            suggested_domain_filter=None,
        )
