import re
from typing import Any, Dict, List, Optional, Union

from src.features.rag.domain.chunk_quality import is_retrievable_chunk
from src.features.rag.domain.hybrid_retrieval import HybridRetrievalResult


class EvidenceEvaluator:
    """Evaluates evidence strength, abstention, and escalation signals from retrieval results."""

    @staticmethod
    def evaluate(
        results: List[Union[HybridRetrievalResult, Dict[str, Any]]],
        query: str,
        jurisdiction: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Deterministically evaluates evidence strength, abstention recommendation,
        human review signal, and generic explainability reasons.
        """
        reasons: List[str] = []

        if not results:
            reasons.append("Zero retrieval results returned.")
            return {
                "strength": "insufficient",
                "abstention_recommended": True,
                "requires_human_review": True,
                "reasons": reasons,
            }

        # Normalize item dictionaries & metadata
        item_dicts: List[Dict[str, Any]] = []
        for item in results:
            if isinstance(item, HybridRetrievalResult):
                item_dicts.append(item.to_dict())
            elif isinstance(item, dict):
                item_dicts.append(item)

        # 1. Filter alignment check
        filter_mismatches = 0
        aligned_items: List[Dict[str, Any]] = []
        for item in item_dicts:
            item_jur = str(item.get("jurisdiction") or item.get("metadata", {}).get("jurisdiction") or "").strip().lower()
            item_dom = str(item.get("domain") or item.get("metadata", {}).get("domain") or "").strip().lower()

            match_jur = True
            if jurisdiction and jurisdiction.strip():
                match_jur = (item_jur == jurisdiction.strip().lower())

            match_dom = True
            if domain and domain.strip():
                match_dom = (item_dom == domain.strip().lower())

            if match_jur and match_dom:
                aligned_items.append(item)
            else:
                filter_mismatches += 1

        if not aligned_items:
            reasons.append("No retrieval results aligned with the requested jurisdiction and domain filters.")
            return {
                "strength": "insufficient",
                "abstention_recommended": True,
                "requires_human_review": True,
                "reasons": reasons,
            }

        if filter_mismatches > 0:
            reasons.append(f"{filter_mismatches} result(s) were excluded due to jurisdiction or domain filter mismatch.")

        # 2. Substantive content check
        substantive_items = [item for item in aligned_items if is_retrievable_chunk(item)]
        substantive_count = len(substantive_items)

        if substantive_count == 0:
            reasons.append("No substantive legal content found among aligned retrieval results.")
            return {
                "strength": "insufficient",
                "abstention_recommended": True,
                "requires_human_review": True,
                "reasons": reasons,
            }

        reasons.append(f"Found {substantive_count} substantive legal result(s).")

        # 3. Score strength & distribution
        top_item = aligned_items[0]
        top_score = float(
            top_item.get("relevance_score")
            or top_item.get("hybrid_score")
            or top_item.get("score")
            or 0.0
        )

        second_score = 0.0
        if len(aligned_items) > 1:
            second_score = float(
                aligned_items[1].get("relevance_score")
                or aligned_items[1].get("hybrid_score")
                or aligned_items[1].get("score")
                or 0.0
            )

        score_margin = top_score - second_score

        # 4. Lexical + Semantic Agreement
        lex_rank = int(top_item.get("lexical_rank", 999))
        sem_rank = int(top_item.get("semantic_rank", 999))
        matched_terms = top_item.get("matched_terms", [])
        has_dual_match = (lex_rank <= 20 and sem_rank <= 20) or bool(matched_terms)

        if has_dual_match:
            reasons.append("Top result demonstrates both lexical and semantic match agreement.")
        else:
            reasons.append("Top result lacks dual lexical and semantic match agreement.")

        # 5. Citation metadata completeness
        has_title = bool(top_item.get("title") or top_item.get("document_id"))
        has_section = bool(top_item.get("section") or top_item.get("chapter") or top_item.get("section_title"))
        metadata_complete = has_title and has_section

        if metadata_complete:
            reasons.append("Top result has complete citation metadata (title and section/chapter).")
        else:
            reasons.append("Top result is missing full citation metadata (section/chapter or title).")

        # Deterministic strength classification
        # Score thresholds based on RRF hybrid scoring scale:
        # Strong: top_score >= 0.025 with dual match or complete metadata
        # Moderate: top_score >= 0.015
        # Weak: top_score >= 0.010
        # Insufficient: top_score < 0.010
        if top_score >= 0.025 and (has_dual_match or metadata_complete) and substantive_count >= 1:
            strength = "strong"
            reasons.append(f"Top retrieval hybrid score ({top_score:.4f}) is strong.")
        elif top_score >= 0.015 and substantive_count >= 1:
            strength = "moderate"
            reasons.append(f"Top retrieval hybrid score ({top_score:.4f}) is moderate.")
        elif top_score >= 0.010:
            strength = "weak"
            reasons.append(f"Top retrieval hybrid score ({top_score:.4f}) is weak.")
        else:
            strength = "insufficient"
            reasons.append(f"Top retrieval hybrid score ({top_score:.4f}) is insufficient.")

        # Abstention decision
        if strength == "insufficient":
            abstention_recommended = True
        elif strength == "weak" and not metadata_complete:
            abstention_recommended = True
            reasons.append("Abstention recommended due to weak retrieval score combined with incomplete citation metadata.")
        elif not metadata_complete and not has_dual_match and strength != "strong":
            abstention_recommended = True
            reasons.append("Abstention recommended due to missing citation metadata and lack of dual match agreement.")
        else:
            abstention_recommended = False

        # Human escalation signal
        requires_human_review = abstention_recommended or (strength in ("weak", "insufficient"))

        return {
            "strength": strength,
            "abstention_recommended": abstention_recommended,
            "requires_human_review": requires_human_review,
            "reasons": reasons,
        }
