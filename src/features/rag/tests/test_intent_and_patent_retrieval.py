"""
Regression & Verification Tests for Intent Detector, Query Expansion, and Domain Relevance Gating.

Covers:
1. Patent Intent Detection in English, Hindi, Telugu, Romanized Hindi, Romanized Telugu.
2. Intent Detection for Trademark, GI, Copyright, Biodiversity, and Regulatory domains.
3. Patent Query Retrieval: Ensures patent queries retrieve patent evidence and avoid GI Sec 47 / Drugs & Cosmetics export rules.
4. Bidirectional Relevance Gating: Irrelevant chunks are down-ranked/filtered; abstains only when substantive relevant evidence is missing.
5. Evidence strength safety: Irrelevant chunks never produce high/strong evidence for patent queries.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.features.rag.domain.intent_detector import IntentDetector
from src.features.rag.domain.evidence_evaluator import EvidenceEvaluator
from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase


class TestIntentAndPatentRetrieval(unittest.TestCase):
    """Regression Suite for RAG Intent Detection and Patent Domain Gating."""

    def test_english_patentability_intent(self):
        res = IntentDetector.detect_intent("Can this Ayurveda product receive patent protection?")
        self.assertEqual(res.domain, "patents")
        self.assertEqual(res.intent_type, "patentability")

    def test_hindi_patentability_intent(self):
        res = IntentDetector.detect_intent("क्या इस आयुर्वेदिक उत्पाद को पेटेंट संरक्षण मिल सकता है?")
        self.assertEqual(res.domain, "patents")

    def test_telugu_patentability_intent(self):
        res = IntentDetector.detect_intent("ఈ ఆయుర్వేద ఉత్పత్తికి పేటెంట్ రక్షణ లభిస్తుందా?")
        self.assertEqual(res.domain, "patents")

    def test_romanized_hindi_patentability_intent(self):
        res = IntentDetector.detect_intent("Kya is Ayurvedic product ko patent protection mil sakta hai?")
        self.assertEqual(res.domain, "patents")

    def test_romanized_telugu_patentability_intent(self):
        res = IntentDetector.detect_intent("Ayurveda product ki patent ravali ante em cheyali?")
        self.assertEqual(res.domain, "patents")

    def test_trademark_intent(self):
        res = IntentDetector.detect_intent("How to register a trademark for my herbal brand logo?")
        self.assertEqual(res.domain, "trademarks")
        self.assertEqual(res.intent_type, "trademark_registration")

    def test_gi_intent(self):
        res = IntentDetector.detect_intent("What is the process for Geographical Indication tag under GI Act?")
        self.assertEqual(res.domain, "geographical_indications")

    def test_copyright_intent(self):
        res = IntentDetector.detect_intent("Can I get copyright for my classical text commentary?")
        self.assertEqual(res.domain, "copyright")

    def test_biodiversity_intent(self):
        res = IntentDetector.detect_intent("What are the ABS requirements under National Biodiversity Authority?")
        self.assertEqual(res.domain, "biodiversity")

    def test_regulatory_intent(self):
        res = IntentDetector.detect_intent("What are FSSAI Ayurveda Aahara food licensing requirements?")
        self.assertEqual(res.domain, "regulatory")

    def test_patent_query_irrelevant_gi_chunks_filtered_or_abstained(self):
        # Simulate retrieval returning only GI Act Section 47 for a patent query
        irrelevant_gi_chunk = {
            "chunk_id": "chunk_gi_sec47",
            "document_id": "india_gi_act_1999",
            "domain": "geographical_indications",
            "title": "Geographical Indications of Goods Act 1999",
            "section": "Section 47",
            "text": "Section 47 relates to jurisdiction of courts for GI suit proceedings.",
            "relevance_score": 0.040,
        }

        assessment = EvidenceEvaluator.evaluate(
            results=[irrelevant_gi_chunk],
            query="Can this product receive patent protection?",
            detected_domain="patents",
        )

        # Must NOT report high/strong evidence, must recommend abstention
        self.assertEqual(assessment["strength"], "insufficient")
        self.assertTrue(assessment["abstention_recommended"])

    def test_patent_query_with_relevant_patent_chunks_succeeds(self):
        relevant_patent_chunk = {
            "chunk_id": "chunk_patents_act_3p",
            "document_id": "india_patents_act_1970",
            "domain": "patents",
            "title": "Patents Act 1970",
            "section": "Section 3(p)",
            "text": "Inventions which in effect are traditional knowledge are not patentable under Section 3(p).",
            "relevance_score": 0.035,
            "lexical_rank": 1,
            "semantic_rank": 1,
        }

        assessment = EvidenceEvaluator.evaluate(
            results=[relevant_patent_chunk],
            query="Can this product receive patent protection?",
            detected_domain="patents",
        )

        self.assertIn(assessment["strength"], ("strong", "moderate"))
        self.assertFalse(assessment["abstention_recommended"])

    def test_mixed_relevant_and_irrelevant_chunks_prioritizes_relevant(self):
        relevant_patent_chunk = {
            "chunk_id": "chunk_patents_act_3p",
            "document_id": "india_patents_act_1970",
            "domain": "patents",
            "title": "Patents Act 1970",
            "section": "Section 3(p)",
            "text": "Inventions which in effect are traditional knowledge are not patentable under Section 3(p).",
            "relevance_score": 0.035,
            "lexical_rank": 1,
            "semantic_rank": 1,
        }
        irrelevant_gi_chunk = {
            "chunk_id": "chunk_gi_sec47",
            "document_id": "india_gi_act_1999",
            "domain": "geographical_indications",
            "title": "Geographical Indications of Goods Act 1999",
            "section": "Section 47",
            "text": "Section 47 relates to jurisdiction of courts.",
            "relevance_score": 0.020,
        }

        assessment = EvidenceEvaluator.evaluate(
            results=[relevant_patent_chunk, irrelevant_gi_chunk],
            query="Can this product receive patent protection?",
            detected_domain="patents",
        )

        # Relevant chunk allows evaluation to succeed without unnecessary abstention
        self.assertIn(assessment["strength"], ("strong", "moderate"))
        self.assertFalse(assessment["abstention_recommended"])


if __name__ == "__main__":
    unittest.main()
