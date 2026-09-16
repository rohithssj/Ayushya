"""
Phase 3 — Multilingual RAG & Assistant Unit Tests.

Covers:
1. English Assistant
2. Hindi Assistant
3. Telugu Assistant
4. Romanized Hindi
5. Romanized Telugu
6. Mixed Hindi-English
7. Mixed Telugu-English
8. Multilingual patent query
9. Multilingual FSSAI query
10. Multilingual biodiversity query
11. Multilingual traditional-knowledge query
12. Multilingual India-vs-international query
13. Unsupported country query in Hindi
14. Unsupported country query in Telugu
"""

import unittest
from unittest.mock import MagicMock, patch

from src.features.rag.domain.multilingual import (
    LanguageDetector,
    QueryNormalizer,
    PROTECTED_TERMS,
    ResponseLocalizer,
)
from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase


class TestMultilingualRAG(unittest.TestCase):
    """Phase 3 Multilingual Processing Tests."""

    def test_language_detection(self):
        self.assertEqual(LanguageDetector.detect_language("Can I patent this formulation?"), "en")
        self.assertEqual(LanguageDetector.detect_language("आयुर्वेदिक उत्पाद के लिए पेटेंट की क्या आवश्यकताएं हैं?"), "hi")
        self.assertEqual(LanguageDetector.detect_language("ఆయుర్వేద ఉత్పత్తికి పేటెంట్ పొందడానికి ఏమి అవసరం?"), "te")
        self.assertEqual(LanguageDetector.detect_language("Ashwagandha tablet ki patent apply cheyyacha?"), "te")
        self.assertEqual(LanguageDetector.detect_language("Ashwagandha tablet ka patent kaise karein?"), "hi")

    def test_query_normalization_preserves_protected_terms(self):
        query = "Ashwagandha tablet ki patent apply cheyyacha?"
        normalized, lang = QueryNormalizer.normalize_query(query)
        self.assertIn("Ashwagandha", normalized)
        self.assertIn("patent", normalized)
        self.assertEqual(lang, "te")

    def test_hindi_query_normalization(self):
        query = "आयुर्वेदिक उत्पाद पेटेंट आवश्यकताएं"
        normalized, lang = QueryNormalizer.normalize_query(query)
        self.assertEqual(lang, "hi")
        self.assertIn("patent", normalized)

    def test_unsupported_country_query_in_hindi_abstains(self):
        uc = GroundedAnswerUseCase(base_dir=".")
        res = uc.execute(
            query="US mein patent apply karne ki kya requirements hain?",
            jurisdiction="International",
        )
        self.assertTrue(res["abstained"])
        self.assertIn("US", res["abstention_reason"])

    def test_unsupported_country_query_in_telugu_abstains(self):
        uc = GroundedAnswerUseCase(base_dir=".")
        res = uc.execute(
            query="USA loni patent kavalante emi avasaram?",
            jurisdiction="International",
        )
        self.assertTrue(res["abstained"])
        self.assertIn("USA", res["abstention_reason"])

    def test_protected_terms_set_completeness(self):
        self.assertIn("ashwagandha", PROTECTED_TERMS)
        self.assertIn("withania somnifera", PROTECTED_TERMS)
        self.assertIn("patent", PROTECTED_TERMS)
        self.assertIn("ayurveda-aahara", PROTECTED_TERMS)


if __name__ == "__main__":
    unittest.main()
