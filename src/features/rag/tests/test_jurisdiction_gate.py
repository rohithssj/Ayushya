"""
Cross-Jurisdiction & Jurisdiction Isolation Gate Tests.

Verifies that:
1. When jurisdiction = INTERNATIONAL, Indian domestic sources are strictly rejected at retrieval, post-retrieval, and evidence selection.
2. CBD and Indian Biological Diversity Act 2002 are never mixed.
3. Nagoya Protocol State obligations are not confused with user obligations.
4. Purely international search queries reject injected Indian legal chunks.
"""

import unittest
from typing import Any, Dict, List

from src.features.rag.domain.evidence_evaluator import EvidenceEvaluator
from src.features.rag.domain.evidence_selector import select_evidence
from src.features.product_analysis.domain.obligation_subject import (
    classify_obligation_subject,
    ObligationSubject,
    is_product_user_obligation,
)


class TestJurisdictionGate(unittest.TestCase):

    def setUp(self):
        self.indian_chunk = {
            "chunk_id": "india_biodiversity_act_2002_sec_3_0001",
            "document_id": "india_biodiversity_act_2002",
            "title": "The Biological Diversity Act, 2002",
            "jurisdiction": "India",
            "domain": "biodiversity",
            "document_type": "Act",
            "text": "3. Certain persons not to undertake Biodiversity related activities without approval of National Biodiversity Authority.",
            "metadata": {"jurisdiction": "India", "domain": "biodiversity"}
        }

        self.cbd_chunk = {
            "chunk_id": "international_cbd_convention_1992_sec_1_0001",
            "document_id": "international_cbd_convention_1992",
            "title": "Convention on Biological Diversity",
            "jurisdiction": "International",
            "domain": "cbd",
            "document_type": "Treaty",
            "text": "Article 1. The objectives of this Convention, to be pursued in accordance with its relevant provisions, are the conservation of biological diversity, the sustainable use of its components and the fair and equitable sharing of the benefits arising out of the utilization of genetic resources.",
            "metadata": {"jurisdiction": "International", "domain": "cbd"}
        }

        self.nagoya_state_chunk = {
            "chunk_id": "international_nagoya_protocol_2010_sec_13_0001",
            "document_id": "international_nagoya_protocol_2010",
            "title": "Nagoya Protocol on Access to Genetic Resources",
            "jurisdiction": "International",
            "domain": "treaties",
            "document_type": "Treaty",
            "text": "Article 13. Each Party shall designate a national focal point on access and benefit-sharing.",
            "metadata": {"jurisdiction": "International", "domain": "treaties"}
        }

    def test_international_jurisdiction_filters_out_indian_chunks(self):
        results = [self.indian_chunk, self.cbd_chunk]
        eval_result = EvidenceEvaluator.evaluate(
            results,
            query="Ashwagandha ABS access requirements",
            jurisdiction="International",
            domain="cbd"
        )
        # Indian chunk must be filtered out
        reasons = " ".join(eval_result.get("reasons", []))
        self.assertIn("excluded due to jurisdiction or domain filter mismatch", reasons)

    def test_evidence_selector_filters_mismatched_jurisdictions(self):
        results = [self.indian_chunk, self.cbd_chunk]
        assessment = {"strength": "strong", "abstention_recommended": False}
        res = select_evidence(results, assessment, jurisdiction="International", max_evidence=5)
        selected = res.get("selected", [])
        selected_jurisdictions = [item.get("citation", {}).get("jurisdiction", "").lower() for item in selected]
        self.assertNotIn("india", selected_jurisdictions)
        self.assertIn("international", selected_jurisdictions)

    def test_obligation_subject_classification(self):
        state_text = "Article 13. Each Party shall designate a national focal point on access and benefit-sharing."
        subj = classify_obligation_subject(state_text)
        self.assertEqual(subj, ObligationSubject.STATE)
        self.assertFalse(is_product_user_obligation(subj))

        user_text = "No person shall export any biological resource without prior approval."
        subj_user = classify_obligation_subject(user_text)
        self.assertEqual(subj_user, ObligationSubject.MANUFACTURER)
        self.assertTrue(is_product_user_obligation(subj_user))


if __name__ == "__main__":
    unittest.main()
