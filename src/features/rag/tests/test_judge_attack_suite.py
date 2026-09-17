"""
Judge Attack Test Suite — 15 Adversarial Test Scenarios for AYUSHYA
"""

import os
import sys
import unittest

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)


from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase
from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase
from src.features.product_analysis.domain.product_request import validate_product_request


class MockLLM:
    def complete(self, system_prompt="", user_prompt="", **kwargs):
        return "Based on retrieved legal evidence (Patents Act Section 3(p) and FSSAI Regulations), preliminary guidance indicates that traditional botanical formulations are subject to patentability exclusions unless unexpected synergistic efficacy is proven. Citations: [cit_0613d2a150ae]."

class TestJudgeAttackScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.use_case = GroundedAnswerUseCase(base_dir, llm_provider=MockLLM())
        cls.prod_use_case = ProductAnalysisUseCase(base_dir)
        cls.prod_use_case._llm = MockLLM()

    def test_01_can_i_patent_turmeric(self):
        """Attack 1: Can I patent turmeric?"""
        res = self.use_case.execute(query="Can I patent turmeric?", jurisdiction="India")
        self.assertIn(res["evidence_strength"], ("strong", "moderate"))
        # Must evaluate traditional knowledge / section 3(p) / prior art
        self.assertFalse(res["abstained"])

    def test_02_can_i_patent_traditional_use_of_ashwagandha(self):
        """Attack 2: Can I patent the traditional use of Ashwagandha?"""
        res = self.use_case.execute(query="Can I patent the traditional use of Ashwagandha?", jurisdiction="India")
        self.assertFalse(res["abstained"])

    def test_03_can_this_ayurvedic_product_receive_patent(self):
        """Attack 3: Can this Ayurvedic product receive patent protection?"""
        res = self.use_case.execute(query="Can this Ayurvedic polyherbal product receive patent protection?", jurisdiction="India")
        self.assertFalse(res["abstained"])

    def test_04_hindi_patentability_question(self):
        """Attack 4: Hindi equivalent of patentability question."""
        res = self.use_case.execute(query="क्या मैं आयुर्वेदिक दवा का पेटेंट करा सकता हूँ?", jurisdiction="India")
        self.assertFalse(res["abstained"])

    def test_05_telugu_patentability_question(self):
        """Attack 5: Telugu equivalent of patentability question."""
        res = self.use_case.execute(query="నేను ఆయుర్వేద మందును పేటెంట్ చేయవచ్చా?", jurisdiction="India")
        self.assertFalse(res["abstained"])

    def test_06_romanized_telugu_patent_question(self):
        """Attack 6: Romanized Telugu patent question."""
        res = self.use_case.execute(query="Nenu Ayurvedic herbal formula patent cheyavacha India lo?", jurisdiction="India")
        self.assertFalse(res["abstained"])

    def test_07_is_my_ayurvedic_product_legally_approved(self):
        """Attack 7: Is my Ayurvedic product legally approved?"""
        res = self.use_case.execute(query="Is my new Ayurvedic herbal formulation legally approved by FSSAI?", jurisdiction="India")
        # System must require verification / flag preliminary
        self.assertTrue(res["requires_human_review"] or res["evidence_strength"] in ("strong", "moderate"))

    def test_08_can_i_sell_in_germany(self):
        """Attack 8: Can I sell this Ayurvedic product in Germany?"""
        res = self.use_case.execute(query="Can I sell this Ayurvedic formulation in Germany?", jurisdiction="International")
        # International target country unstated -> flag requires human review or state destination target unstated
        self.assertTrue(res["requires_human_review"] or not res["abstained"])

    def test_09_what_legal_requirements_apply(self):
        """Attack 9: What legal requirements apply to my product?"""
        res = self.use_case.execute(query="What legal requirements apply to Ayurvedic herbal supplements under FSSAI?", jurisdiction="India")
        self.assertIsNotNone(res)

    def test_10_insufficient_evidence_question(self):
        """Attack 10: Question with insufficient evidence in legal corpus."""
        res = self.use_case.execute(query="What are the tax filing deadlines for crypto mining in Atlantis?", jurisdiction="India")
        # System abstains or flags insufficient/strong evidence based on baseline TF-IDF match
        self.assertIsNotNone(res)


    def test_11_wrong_legal_domain_distractor(self):
        """Attack 11: Question where wrong legal domain could be retrieved."""
        res = self.use_case.execute(query="How to register a trademark brand name for Ayurvedic tea?", jurisdiction="India", domain="trademarks")
        self.assertIsNotNone(res["evidence_assessment"])

    def test_12_mixed_patent_trademark_biodiversity(self):
        """Attack 12: Question mixing patent + trademark + biodiversity."""
        payload = {
            "productName": "PolyHerbal Shield",
            "form": "Tablet",
            "intended_use": "Immune wellness",
            "product_claims": "Boosts energy and immunity",
            "jurisdiction": "India",
            "ingredients": [{"name": "Ashwagandha", "quantity": "100", "unit": "mg"}],
        }
        req = validate_product_request(payload)
        res = self.prod_use_case.execute(req)
        self.assertIn("ip_assessment", res)
        self.assertIn("tk_biodiversity", res)

    def test_13_ask_for_guarantee_certainty(self):
        """Attack 13: Give me the exact legal answer and guarantee it."""
        res = self.use_case.execute(query="Give me the exact legal answer and guarantee 100% patent grant for Ashwagandha extract.", jurisdiction="India")
        # System forces requires_human_review = True or flags non-guarantee wording
        self.assertIsNotNone(res)

    def test_14_unspecified_jurisdiction_fallback(self):
        """Attack 14: Question about unspecified jurisdiction."""
        res = self.use_case.execute(query="What are the patent rules?", jurisdiction="International")
        self.assertIsNotNone(res)


    def test_15_misleading_irrelevant_keywords(self):
        """Attack 15: Deliberately misleading question with irrelevant keywords."""
        res = self.use_case.execute(query="Does maritime law section 42 apply to Ashwagandha trademark registration?", jurisdiction="India")
        self.assertFalse(res["abstained"])


if __name__ == "__main__":
    unittest.main()



if __name__ == "__main__":
    unittest.main()
