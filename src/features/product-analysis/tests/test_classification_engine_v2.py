"""
Regression Test Suite — AYUSHYA Formulation Classification Engine v2 (TEST 1 to TEST 10)
"""

import unittest
from src.features.product_analysis.domain.product_request import (
    validate_product_request,
    ProductAnalysisRequest,
    IngredientRecord,
)
from src.features.product_analysis.domain.domain_router import DomainRouter
from src.features.product_analysis.domain.query_builder import QueryBuilder
from src.features.product_analysis.application.structured_response_parser import (
    parse_structured_analysis_response,
)


class TestClassificationEngineV2(unittest.TestCase):

    def test_1_ashwagandha_wellness_no_preference(self):
        """TEST 1: Ashwagandha tablet, wellness claims, no disease claim, no preference -> Independent assessment."""
        raw = {
            "productName": "Ashwagandha Wellness Tablet",
            "form": "Tablet",
            "intended_use": "Daily wellness product for general immune and stress support.",
            "product_claims": "Supports immunity and stress management.",
            "category": "No preference — let AYUSHYA assess",
            "ingredients": [{"name": "Ashwagandha", "quantity": "500", "unit": "mg"}],
            "jurisdiction": "India",
        }
        req = validate_product_request(raw)
        self.assertEqual(req.user_selected_classification, "No preference — let AYUSHYA assess")

        router = DomainRouter()
        dims = router.route(req)
        legal_domains = [d.legal_domain for d in dims]

        # Independent multi-domain routing should query both food and drugs-cosmetics
        self.assertIn("ayurveda-aahar", legal_domains)
        self.assertIn("drugs-cosmetics", legal_domains)
        self.assertIn("patents", legal_domains)

    def test_2_same_product_user_proposes_ayurveda_aahar(self):
        """TEST 2: Same product, user proposes Ayurveda-Aahar -> Proposal separate, retrieval not restricted."""
        raw = {
            "productName": "Ashwagandha Wellness Tablet",
            "form": "Tablet",
            "intended_use": "Daily wellness product for general immune and stress support.",
            "category": "Ayurveda-Aahar",
            "ingredients": [{"name": "Ashwagandha", "quantity": "500", "unit": "mg"}],
            "jurisdiction": "India",
        }
        req = validate_product_request(raw)
        self.assertEqual(req.user_selected_classification, "Ayurveda-Aahar")

        router = DomainRouter()
        dims = router.route(req)
        legal_domains = [d.legal_domain for d in dims]

        # Retrieval is NOT restricted to ayurveda-aahar; drugs-cosmetics & patents are also routed
        self.assertIn("ayurveda-aahar", legal_domains)
        self.assertIn("drugs-cosmetics", legal_domains)

    def test_3_user_proposes_proprietary_ayurvedic(self):
        """TEST 3: User proposes Proprietary Ayurvedic Formulation -> Proposal does not become conclusion."""
        raw = {
            "productName": "Herbal Wellness Tablet",
            "form": "Tablet",
            "intended_use": "General health supplement.",
            "category": "Proprietary Ayurvedic Formulation",
            "ingredients": [{"name": "Tulsi", "quantity": "100", "unit": "mg"}],
            "jurisdiction": "India",
        }
        req = validate_product_request(raw)
        self.assertEqual(req.user_selected_classification, "Proprietary Ayurvedic Formulation")

        parsed_llm = {
            "grounded_summary": "Preliminary analysis of the formulation.",
            "classification": {
                "user_selected": "Proprietary Ayurvedic Formulation",
                "preliminary_assessment": "Potentially applicable under Ayurveda-Aahar or Proprietary ASU framework.",
                "evidence_strength": "moderate",
                "primary": {
                    "category": "Ayurveda-Aahar",
                    "status": "potentially_applicable",
                    "reasoning": "Formulation intended for general health wellness."
                }
            }
        }
        validated = parse_structured_analysis_response(str(parsed_llm).replace("'", '"'), set())
        # User selected proposal is separate from primary assessment
        self.assertEqual(validated["classification"]["user_selected"], "Proprietary Ayurvedic Formulation")
        self.assertEqual(validated["classification"]["primary"]["category"], "Ayurveda-Aahar")

    def test_4_missing_classical_reference_prevents_false_conclusion(self):
        """TEST 4: User proposes Classical Ayurvedic Formulation without reference -> Missing info flagged."""
        raw = {
            "productName": "Classic Churna",
            "form": "Syrup / Churna",
            "intended_use": "Digestive wellness.",
            "category": "Classical Ayurvedic Formulation",
            "is_classical_basis": "yes",
            "classical_reference": "", # missing reference source!
            "ingredients": [{"name": "Triphala", "quantity": "1", "unit": "g"}],
            "jurisdiction": "India",
        }
        req = validate_product_request(raw)
        self.assertEqual(req.is_classical_basis, "yes")
        self.assertIsNone(req.classical_reference)

        parsed_llm = {
            "classification": {
                "user_selected": "Classical Ayurvedic Formulation",
                "preliminary_assessment": "Classical basis claimed but exact textual reference was not supplied.",
                "evidence_strength": "weak",
                "primary": {
                    "category": "Classical Ayurvedic Formulation",
                    "status": "not_established",
                    "reasoning": "Cannot be independently established as classical without authoritative text citation."
                },
                "missing_information": ["Exact classical Ayurvedic reference text (e.g. Sahasrayogam or Charaka Samhita)"]
            }
        }
        validated = parse_structured_analysis_response(str(parsed_llm).replace("'", '"'), set())
        self.assertEqual(validated["classification"]["primary"]["status"], "not_established")
        self.assertGreater(len(validated["classification"]["missing_information"]), 0)

    def test_5_botanical_tablet_with_disease_claim(self):
        """TEST 5: Botanical tablet + disease claim -> Disease claim surfaced, regulatory domains routed, no automatic drug conclusion."""
        raw = {
            "productName": "Anti-Diabetes Herbal Tablet",
            "form": "Tablet",
            "intended_use": "Formulation for blood sugar management.",
            "disease_claim_flag": True,
            "disease_claim_text": "Helps treat and cure diabetes mellitus.",
            "ingredients": [{"name": "Karela", "quantity": "250", "unit": "mg"}],
            "jurisdiction": "India",
        }
        req = validate_product_request(raw)
        self.assertTrue(req.disease_claim_flag)

        router = DomainRouter()
        dims = router.route(req)
        legal_domains = [d.legal_domain for d in dims]

        # Must route to drugs-cosmetics due to disease claim
        self.assertIn("drugs-cosmetics", legal_domains)

    def test_6_topical_botanical_product_cosmetic(self):
        """TEST 6: Topical botanical product with cosmetic intended use -> Cosmetic framework considered."""
        raw = {
            "productName": "Herbal Glow Cream",
            "form": "Cosmetic Cream",
            "intended_use": "Topical cream for skin moisturizing and facial complexion enhancement.",
            "ingredients": [{"name": "Kumkuma", "quantity": "10", "unit": "mg"}],
            "jurisdiction": "India",
        }
        req = validate_product_request(raw)
        self.assertEqual(req.product_form, "Cosmetic Cream")

        router = DomainRouter()
        dims = router.route(req)
        legal_domains = [d.legal_domain for d in dims]

        self.assertIn("drugs-cosmetics", legal_domains)

    def test_7_oral_botanical_wellness_product(self):
        """TEST 7: Oral botanical wellness product -> Food/Ayurveda-Aahar and drug-related frameworks considered."""
        raw = {
            "productName": "Brahmi Memory Support",
            "form": "Capsule",
            "intended_use": "Oral dietary supplement for cognitive support.",
            "ingredients": [{"name": "Brahmi (Bacopa monnieri)", "quantity": "300", "unit": "mg"}],
            "jurisdiction": "India",
        }
        req = validate_product_request(raw)
        router = DomainRouter()
        dims = router.route(req)
        legal_domains = [d.legal_domain for d in dims]

        self.assertIn("ayurveda-aahar", legal_domains)
        self.assertIn("drugs-cosmetics", legal_domains)

    def test_8_no_preference_default(self):
        """TEST 8: 'No preference' -> No user hypothesis influences classification."""
        raw = {
            "productName": "Generic Herbal Blend",
            "form": "Powder",
            "intended_use": "General health supplement.",
            "category": "No preference — let AYUSHYA assess",
            "ingredients": [{"name": "Amla", "quantity": "500", "unit": "mg"}],
            "jurisdiction": "India",
        }
        req = validate_product_request(raw)
        self.assertEqual(req.user_selected_classification, "No preference — let AYUSHYA assess")

    def test_9_ambiguous_product_returns_alternatives(self):
        """TEST 9: Ambiguous product -> Multiple potentially relevant categories returned."""
        parsed_llm = {
            "classification": {
                "user_selected": "No preference — let AYUSHYA assess",
                "preliminary_assessment": "Product exhibits features of both Ayurveda-Aahar and Proprietary ASU Medicine.",
                "evidence_strength": "moderate",
                "primary": {
                    "category": "Ayurveda-Aahar",
                    "status": "potentially_applicable",
                    "reasoning": "Formulation is marketed as a general dietary food supplement."
                },
                "alternatives": [
                    {
                        "category": "Proprietary Ayurvedic Formulation",
                        "status": "potentially_applicable",
                        "reasoning": "Dosage form (tablet) and standardized extract processing may engage ASU Drug provisions."
                    }
                ]
            }
        }
        validated = parse_structured_analysis_response(str(parsed_llm).replace("'", '"'), set())
        self.assertEqual(validated["classification"]["primary"]["category"], "Ayurveda-Aahar")
        self.assertEqual(len(validated["classification"]["alternatives"]), 1)
        self.assertEqual(validated["classification"]["alternatives"][0]["category"], "Proprietary Ayurvedic Formulation")

    def test_10_insufficient_product_facts(self):
        """TEST 10: Insufficient product facts -> Classification = insufficient_evidence / not_established with missing info."""
        raw = {
            "productName": "Mystery Powder",
            "form": "Powder",
            "intended_use": "General wellness",
            "ingredients": [{"name": "Herb X", "quantity": "100", "unit": "mg"}],
            "jurisdiction": "India",
        }
        req = validate_product_request(raw)
        parsed_llm = {
            "classification": {
                "user_selected": "No preference — let AYUSHYA assess",
                "preliminary_assessment": "Insufficient evidence to establish classification for unverified ingredient Herb X.",
                "evidence_strength": "insufficient",
                "primary": {
                    "category": "Not Established",
                    "status": "insufficient_evidence",
                    "reasoning": "Ingredient identity and regulatory status under Ayurvedic Pharmacopoeia / FSSAI could not be established."
                },
                "missing_information": ["Botanical name of Herb X", "Extraction ratio and manufacturing method"]
            }
        }
        validated = parse_structured_analysis_response(str(parsed_llm).replace("'", '"'), set())
        self.assertEqual(validated["classification"]["primary"]["status"], "insufficient_evidence")
        self.assertEqual(len(validated["classification"]["missing_information"]), 2)
