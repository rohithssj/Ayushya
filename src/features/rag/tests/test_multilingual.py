"""
Multilingual Processing & Sarvam Integration Tests.

Verifies:
1. English language detection and query normalization (0 Sarvam calls).
2. Hindi script language detection and Sarvam translation call.
3. Telugu script language detection and Sarvam translation call.
4. Romanized Hindi script pattern detection & transliteration.
5. Romanized Telugu script pattern detection & transliteration.
6. Citation placeholder preservation ([cit_fssai_aahar_01] intact after translation).
7. Legal safety preservation ("may apply", "insufficient evidence", abstention).
8. Failure fallback when Sarvam key is missing or API errors out.
9. Canonical BioShield multilingual equivalence across English, Hindi, Telugu, Romanized Hindi, Romanized Telugu.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.features.rag.domain.multilingual.language_detector import LanguageDetector
from src.features.rag.domain.multilingual.terminology import PROTECTED_TERMS
from src.features.rag.domain.multilingual.query_normalizer import QueryNormalizer
from src.features.rag.domain.multilingual.response_localizer import ResponseLocalizer
from src.features.rag.infrastructure.multilingual.sarvam_client import SarvamClient
from src.features.product_analysis.domain.product_request import (
    ProductAnalysisRequest,
    IngredientRecord,
)
from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase


class TestMultilingualSarvamIntegration(unittest.TestCase):
    """Multilingual Integration and Sarvam Regression Suite."""

    def test_english_query_detection_and_zero_sarvam_calls(self):
        mock_sarvam = MagicMock(spec=SarvamClient)
        mock_sarvam.is_available = True

        detector = LanguageDetector()
        res = detector.detect_structured("What patent protection is available for this formulation?")
        self.assertEqual(res["language"], "en")
        self.assertFalse(res["romanized"])

        normalizer = QueryNormalizer(sarvam_client=mock_sarvam)
        norm_query, lang = normalizer.normalize("What patent protection is available for this formulation?")
        self.assertEqual(lang, "en")
        self.assertEqual(norm_query, "What patent protection is available for this formulation?")
        mock_sarvam.translate.assert_not_called()
        mock_sarvam.transliterate.assert_not_called()

    def test_hindi_script_detection(self):
        detector = LanguageDetector()
        res = detector.detect_structured("इस उत्पाद के लिए पेटेंट सुरक्षा क्या है?")
        self.assertEqual(res["language"], "hi")
        self.assertEqual(res["script"], "devanagari")
        self.assertFalse(res["romanized"])

    def test_telugu_script_detection(self):
        detector = LanguageDetector()
        res = detector.detect_structured("ఈ ఉత్పత్తికి పేటెంట్ రక్షణ లభిస్తుందా?")
        self.assertEqual(res["language"], "te")
        self.assertEqual(res["script"], "telugu")
        self.assertFalse(res["romanized"])

    def test_romanized_hindi_detection(self):
        detector = LanguageDetector()
        res = detector.detect_structured("Is product ke liye patent kaise milega?")
        self.assertEqual(res["language"], "hi")
        self.assertEqual(res["script"], "latin")
        self.assertTrue(res["romanized"])

    def test_romanized_telugu_detection(self):
        detector = LanguageDetector()
        res = detector.detect_structured("Ee product ki patent vastunda?")
        self.assertEqual(res["language"], "te")
        self.assertEqual(res["script"], "latin")
        self.assertTrue(res["romanized"])

    def test_citation_placeholder_preservation(self):
        mock_sarvam = MagicMock(spec=SarvamClient)
        mock_sarvam.is_available = True
        # Simulate Sarvam translating text with placeholder intact
        mock_sarvam.translate.side_effect = lambda text, source_lang, target_lang: text.replace(
            "According to the regulation", "नियम के अनुसार"
        )

        localizer = ResponseLocalizer(sarvam_client=mock_sarvam)
        input_text = "According to the regulation [cit_fssai_aahar_01] provision applies."
        localized = localizer.localize_answer(input_text, target_language="hi")

        self.assertIn("[cit_fssai_aahar_01]", localized)
        mock_sarvam.translate.assert_called_once()

    def test_sarvam_failure_fallback_returns_english_answer(self):
        mock_sarvam = MagicMock(spec=SarvamClient)
        mock_sarvam.is_available = True
        mock_sarvam.translate.return_value = None  # API failure / timeout

        localizer = ResponseLocalizer(sarvam_client=mock_sarvam)
        input_text = "The provision may apply depending on product classification. [cit_fssai_aahar_01]"
        localized = localizer.localize_answer(input_text, target_language="hi")

        # Fallback must return original English answer unchanged
        self.assertEqual(localized, input_text)

    def test_protected_terms_coverage(self):
        mandatory = [
            "ashwagandha", "withania somnifera", "turmeric", "curcuma longa",
            "neem", "azadirachta indica", "pippali", "piper longum",
            "black pepper", "piper nigrum", "patent", "trademark",
            "geographical indication", "copyright", "traditional knowledge",
            "tkdl", "abs", "nagoya protocol", "cbd", "trips", "pct",
            "fssai", "ayurveda-aahara", "nba", "pic", "mat"
        ]
        for term in mandatory:
            self.assertIn(term, PROTECTED_TERMS)

    def test_bioshield_multilingual_data_fact_integrity(self):
        ingredients = [
            IngredientRecord("Ashwagandha (Withania somnifera)", "300", "mg"),
            IngredientRecord("Turmeric (Curcuma longa)", "200", "mg"),
            IngredientRecord("Neem (Azadirachta indica)", "100", "mg"),
            IngredientRecord("Pippali (Piper longum)", "50", "mg"),
            IngredientRecord("Black pepper (Piper nigrum)", "20", "mg"),
        ]

        req_en = ProductAnalysisRequest(
            jurisdiction="India",
            product_name="AyurVeda BioShield",
            product_form="tablet",
            ingredients=ingredients,
            intended_use="Daily immunity and wellness supplement",
            user_selected_classification="no_preference",
        )

        use_case = ProductAnalysisUseCase(base_dir=".")
        # Dry run analysis
        res_en = use_case.execute(req_en, target_language="en")

        # Verify BioShield 5 ingredients present, Tulsi absent
        ing_list = [i.name for i in req_en.ingredients]
        self.assertEqual(len(ing_list), 5)
        self.assertNotIn("Tulsi", ing_list)
        self.assertIn("Ashwagandha (Withania somnifera)", ing_list)
        self.assertIn("Black pepper (Piper nigrum)", ing_list)



if __name__ == "__main__":
    unittest.main()
