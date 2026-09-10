"""
Phase 7 — Evidence Selection + Citation Construction: deterministic unit tests.

All tests use synthetic data; no real corpus required.
Tests 1-14 as specified in the Phase 7 task.
"""

import unittest
from src.features.rag.domain.evidence_selector import (
    build_citation,
    select_evidence,
    _chunk_id,
)
from src.features.rag.domain.evidence_evaluator import EvidenceEvaluator
from src.features.rag.domain.hybrid_retrieval import HybridRetrievalResult


# ---------------------------------------------------------------------------
# Shared synthetic test data helpers
# ---------------------------------------------------------------------------

def _make_chunk(
    chunk_id="c001",
    jurisdiction="india",
    domain="patents",
    section="Section 3",
    section_title="Non-patentable inventions",
    subsection="3(d)",
    chapter="Chapter II",
    page_start=12,
    page_end=13,
    authority="Parliament of India",
    year=1970,
    source_url="https://ipindia.gov.in/patents-act.pdf",
    text=None,
):
    if text is None:
        text = (
            "The following shall not be inventions within the meaning of this Act: "
            "the mere discovery of a new form of a known substance which does not result "
            "in the enhancement of the known efficacy of that substance."
        )
    return {
        "chunk_id": chunk_id,
        "document_id": "patents_act_1970",
        "title": "The Patents Act, 1970",
        "jurisdiction": jurisdiction,
        "domain": domain,
        "section": section,
        "section_title": section_title,
        "subsection": subsection,
        "chapter": chapter,
        "page_start": page_start,
        "page_end": page_end,
        "authority": authority,
        "year": year,
        "source_url": source_url,
        "text": text,
        "relevance_score": 0.045,
        "lexical_rank": 1,
        "semantic_rank": 2,
        "matched_terms": ["patent", "substance"],
        "rank": 1,
    }


def _strong_assessment():
    return {
        "strength": "strong",
        "abstention_recommended": False,
        "requires_human_review": False,
        "reasons": ["Found 1 substantive legal result(s)."],
    }


def _insufficient_assessment():
    return {
        "strength": "insufficient",
        "abstention_recommended": True,
        "requires_human_review": True,
        "reasons": ["Zero retrieval results returned."],
    }


def _weak_assessment(abstain=False):
    return {
        "strength": "weak",
        "abstention_recommended": abstain,
        "requires_human_review": True,
        "reasons": ["Top retrieval hybrid score is weak."],
    }


# ===========================================================================
# Test 1: Selects substantive evidence
# ===========================================================================
class TestSelectsSubstantiveEvidence(unittest.TestCase):
    def test_selects_substantive_chunk(self):
        chunk = _make_chunk()
        evidence = select_evidence([chunk], _strong_assessment(), "india", "patents")
        self.assertEqual(evidence["count"], 1)
        self.assertEqual(evidence["selected"][0]["chunk_id"], "c001")

    def test_excludes_non_substantive_chunk(self):
        # Headings-only chunk (very short, no legal keyword, is heading-like)
        short_chunk = _make_chunk(
            chunk_id="c_short",
            text="Chapter II",
            section="Chapter II",
            section_title="Chapter II",
        )
        evidence = select_evidence([short_chunk], _strong_assessment(), "india", "patents")
        # is_retrievable_chunk should reject this
        self.assertEqual(evidence["count"], 0)


# ===========================================================================
# Test 2: Removes duplicate chunk IDs
# ===========================================================================
class TestDeduplication(unittest.TestCase):
    def test_deduplicates_same_chunk_id(self):
        chunk1 = _make_chunk(chunk_id="c001")
        chunk2 = dict(chunk1)  # same chunk_id
        chunk2["rank"] = 2
        evidence = select_evidence([chunk1, chunk2], _strong_assessment(), "india", "patents")
        self.assertEqual(evidence["count"], 1)
        self.assertEqual(evidence["selected"][0]["chunk_id"], "c001")

    def test_allows_distinct_chunk_ids(self):
        chunk1 = _make_chunk(chunk_id="c001")
        chunk2 = _make_chunk(
            chunk_id="c002",
            section="Section 5",
            section_title="Inventions not patentable",
            text=(
                "No patent shall be granted in respect of an invention relating to "
                "atomic energy falling within sub-section (1) of section 20 of the "
                "Atomic Energy Act, 1962."
            ),
        )
        chunk2["rank"] = 2
        evidence = select_evidence([chunk1, chunk2], _strong_assessment(), "india", "patents")
        self.assertEqual(evidence["count"], 2)


# ===========================================================================
# Test 3: Preserves ranking order deterministically
# ===========================================================================
class TestRankingOrder(unittest.TestCase):
    def test_preserves_input_order(self):
        chunk1 = _make_chunk(chunk_id="c001")
        chunk2 = _make_chunk(
            chunk_id="c002",
            text="A patent application shall be made in the prescribed form.",
        )
        chunk2["rank"] = 2
        evidence = select_evidence([chunk1, chunk2], _strong_assessment(), "india", "patents")
        ids = [e["chunk_id"] for e in evidence["selected"]]
        self.assertEqual(ids, ["c001", "c002"])

    def test_deterministic_evidence_ids(self):
        chunk = _make_chunk()
        ev1 = select_evidence([chunk], _strong_assessment(), "india", "patents")
        ev2 = select_evidence([chunk], _strong_assessment(), "india", "patents")
        self.assertEqual(
            ev1["selected"][0]["evidence_id"],
            ev2["selected"][0]["evidence_id"],
        )


# ===========================================================================
# Test 4: Builds citations from actual chunk metadata
# ===========================================================================
class TestCitationBuilding(unittest.TestCase):
    def test_citation_built_from_metadata(self):
        chunk = _make_chunk()
        citation = build_citation(chunk, "cit_test001")
        self.assertEqual(citation["citation_id"], "cit_test001")
        self.assertEqual(citation["document_id"], "patents_act_1970")
        self.assertEqual(citation["title"], "The Patents Act, 1970")
        self.assertEqual(citation["chunk_id"], "c001")
        self.assertEqual(citation["jurisdiction"], "india")
        self.assertEqual(citation["domain"], "patents")

    def test_citation_in_selected_evidence(self):
        chunk = _make_chunk()
        evidence = select_evidence([chunk], _strong_assessment(), "india", "patents")
        self.assertIn("citation", evidence["selected"][0])
        cit = evidence["selected"][0]["citation"]
        self.assertTrue(cit["citation_id"].startswith("cit_"))


# ===========================================================================
# Test 5: Preserves section/chapter/subsection/page metadata
# ===========================================================================
class TestMetadataPreservation(unittest.TestCase):
    def test_section_fields_preserved(self):
        chunk = _make_chunk()
        citation = build_citation(chunk, "cit_x")
        self.assertEqual(citation["section"], "Section 3")
        self.assertEqual(citation["section_title"], "Non-patentable inventions")
        self.assertEqual(citation["subsection"], "3(d)")
        self.assertEqual(citation["chapter"], "Chapter II")
        self.assertEqual(citation["page_start"], 12)
        self.assertEqual(citation["page_end"], 13)
        self.assertEqual(citation["authority"], "Parliament of India")
        self.assertEqual(citation["year"], 1970)


# ===========================================================================
# Test 6: Does not fabricate missing metadata
# ===========================================================================
class TestNoFabricatedMetadata(unittest.TestCase):
    def test_missing_section_is_none(self):
        chunk = _make_chunk()
        chunk.pop("section", None)
        chunk.pop("section_title", None)
        chunk.pop("chapter", None)
        citation = build_citation(chunk, "cit_x")
        self.assertIsNone(citation["section"])
        self.assertIsNone(citation["section_title"])
        self.assertIsNone(citation["chapter"])

    def test_missing_year_is_none(self):
        chunk = _make_chunk()
        chunk.pop("year", None)
        citation = build_citation(chunk, "cit_x")
        self.assertIsNone(citation["year"])

    def test_missing_authority_is_none(self):
        chunk = _make_chunk()
        chunk.pop("authority", None)
        citation = build_citation(chunk, "cit_x")
        self.assertIsNone(citation["authority"])


# ===========================================================================
# Test 7: Does not fabricate source URLs
# ===========================================================================
class TestNoFabricatedSourceUrl(unittest.TestCase):
    def test_source_url_preserved_when_present(self):
        chunk = _make_chunk(source_url="https://ipindia.gov.in/patents-act.pdf")
        citation = build_citation(chunk, "cit_x")
        self.assertEqual(citation["source_url"], "https://ipindia.gov.in/patents-act.pdf")

    def test_source_url_none_when_absent(self):
        chunk = _make_chunk()
        chunk.pop("source_url", None)
        citation = build_citation(chunk, "cit_x")
        self.assertIsNone(citation["source_url"])

    def test_source_url_none_when_empty_string(self):
        chunk = _make_chunk(source_url="")
        citation = build_citation(chunk, "cit_x")
        self.assertIsNone(citation["source_url"])

    def test_source_url_none_when_explicitly_null(self):
        chunk = _make_chunk()
        chunk["source_url"] = None
        citation = build_citation(chunk, "cit_x")
        self.assertIsNone(citation["source_url"])


# ===========================================================================
# Test 8: Respects jurisdiction filter
# ===========================================================================
class TestJurisdictionFilter(unittest.TestCase):
    def test_excludes_wrong_jurisdiction(self):
        chunk = _make_chunk(jurisdiction="international")
        evidence = select_evidence([chunk], _strong_assessment(), "india", "patents")
        self.assertEqual(evidence["count"], 0)

    def test_includes_correct_jurisdiction(self):
        chunk = _make_chunk(jurisdiction="india")
        evidence = select_evidence([chunk], _strong_assessment(), "india", "patents")
        self.assertEqual(evidence["count"], 1)


# ===========================================================================
# Test 9: Respects domain filter
# ===========================================================================
class TestDomainFilter(unittest.TestCase):
    def test_excludes_wrong_domain(self):
        chunk = _make_chunk(domain="trademarks")
        evidence = select_evidence([chunk], _strong_assessment(), "india", "patents")
        self.assertEqual(evidence["count"], 0)

    def test_includes_correct_domain(self):
        chunk = _make_chunk(domain="patents")
        evidence = select_evidence([chunk], _strong_assessment(), "india", "patents")
        self.assertEqual(evidence["count"], 1)


# ===========================================================================
# Test 10: Handles zero results
# ===========================================================================
class TestZeroResults(unittest.TestCase):
    def test_empty_results_returns_empty_evidence(self):
        evidence = select_evidence([], _insufficient_assessment(), "india", "patents")
        self.assertEqual(evidence["count"], 0)
        self.assertEqual(evidence["selected"], [])


# ===========================================================================
# Test 11: Handles insufficient evidence
# ===========================================================================
class TestInsufficientEvidence(unittest.TestCase):
    def test_insufficient_strength_returns_empty(self):
        chunk = _make_chunk()
        evidence = select_evidence([chunk], _insufficient_assessment(), "india", "patents")
        self.assertEqual(evidence["count"], 0)
        self.assertEqual(evidence["selected"], [])

    def test_abstention_with_insufficient_strength_returns_empty(self):
        chunk = _make_chunk()
        assessment = {
            "strength": "insufficient",
            "abstention_recommended": True,
            "requires_human_review": True,
            "reasons": ["Score too low."],
        }
        evidence = select_evidence([chunk], assessment, "india", "patents")
        self.assertEqual(evidence["count"], 0)


# ===========================================================================
# Test 12: Handles weak evidence
# ===========================================================================
class TestWeakEvidence(unittest.TestCase):
    def test_weak_non_abstaining_selects_evidence(self):
        chunk = _make_chunk()
        # weak but abstention not recommended — should still select usable evidence
        assessment = _weak_assessment(abstain=False)
        evidence = select_evidence([chunk], assessment, "india", "patents")
        self.assertEqual(evidence["count"], 1)

    def test_weak_with_abstention_returns_empty(self):
        chunk = _make_chunk()
        assessment = _weak_assessment(abstain=True)
        evidence = select_evidence([chunk], assessment, "india", "patents")
        self.assertEqual(evidence["count"], 0)


# ===========================================================================
# Test 13: Every citation maps to an actual selected chunk
# ===========================================================================
class TestCitationChunkMapping(unittest.TestCase):
    def test_every_citation_maps_to_selected_chunk(self):
        chunk1 = _make_chunk(chunk_id="c001")
        chunk2 = _make_chunk(
            chunk_id="c002",
            section="Section 5",
            text="A patent application shall be made in the prescribed form and manner.",
        )
        chunk2["rank"] = 2
        evidence = select_evidence([chunk1, chunk2], _strong_assessment(), "india", "patents")

        selected_chunk_ids = {e["chunk_id"] for e in evidence["selected"]}
        for ev in evidence["selected"]:
            cit_chunk_id = ev["citation"]["chunk_id"]
            self.assertIn(
                cit_chunk_id,
                selected_chunk_ids,
                f"Citation chunk_id '{cit_chunk_id}' does not match any selected evidence chunk.",
            )
            # citation chunk_id must match the evidence item's own chunk_id
            self.assertEqual(ev["chunk_id"], cit_chunk_id)

    def test_count_matches_selected_length(self):
        chunk = _make_chunk()
        evidence = select_evidence([chunk], _strong_assessment(), "india", "patents")
        self.assertEqual(evidence["count"], len(evidence["selected"]))


# ===========================================================================
# Test 14: Existing retrieval/evidence evaluator behavior unchanged
# ===========================================================================
class TestExistingBehaviorUnchanged(unittest.TestCase):
    def test_evidence_evaluator_still_works(self):
        """EvidenceEvaluator must still return the same contract as Phase 6."""
        chunk = {
            "chunk_id": "legacy_001",
            "document_id": "patents_act_1970",
            "title": "The Patents Act, 1970",
            "section": "Section 3",
            "jurisdiction": "india",
            "domain": "patents",
            "text": (
                "The following shall not be inventions within the meaning of this Act: "
                "a substance obtained by a mere admixture."
            ),
        }
        item = HybridRetrievalResult(
            chunk=chunk,
            hybrid_score=0.045,
            lexical_rank=1,
            semantic_rank=1,
            matched_terms=("patent",),
        )
        result = EvidenceEvaluator.evaluate(
            results=[item],
            query="patentability herbal",
            jurisdiction="india",
            domain="patents",
        )
        self.assertIn("strength", result)
        self.assertIn("abstention_recommended", result)
        self.assertIn("requires_human_review", result)
        self.assertIn("reasons", result)
        self.assertIsInstance(result["reasons"], list)

    def test_hybrid_retrieval_result_to_dict_unchanged(self):
        """HybridRetrievalResult.to_dict() contract must remain intact."""
        chunk = {"chunk_id": "c000", "text": "test", "jurisdiction": "india", "domain": "patents"}
        item = HybridRetrievalResult(
            chunk=chunk, hybrid_score=0.03, lexical_rank=2, semantic_rank=3,
            matched_terms=("test",),
        )
        d = item.to_dict()
        self.assertIn("relevance_score", d)
        self.assertIn("lexical_rank", d)
        self.assertIn("semantic_rank", d)
        self.assertIn("matched_terms", d)


if __name__ == "__main__":
    unittest.main()
