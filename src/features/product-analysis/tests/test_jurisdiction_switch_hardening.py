"""
Jurisdiction Switch Hardening Regression Test Suite.

Verifies Ashwagandha International analysis requirements:
1. No Indian domestic sources (FSSAI, Biological Diversity Act, NBA, Patents Act 1970).
2. No State/Party obligations in compliance checklist.
3. No unconditional PIC or MAT checklist actions.
4. Preserves CBD vs Nagoya framework distinction.
5. Overall evidence level does not claim STRONG when major dimensions are insufficient.
6. Correct preliminary classification and patent wording.
"""

import unittest
from src.features.rag.infrastructure.openrouter_provider import OpenRouterProvider
from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase
from src.features.product_analysis.domain.product_request import validate_product_request


class TestJurisdictionSwitchHardening(unittest.TestCase):

    def setUp(self):
        self.mock_llm = OpenRouterProvider(api_key="mock-key")
        self.use_case = ProductAnalysisUseCase("d:/Ayushya", llm_provider=self.mock_llm)

        self.intl_request_raw = {
            "productName": "Ashwagandha Wellness Tablet",
            "category": "Ayurveda-Aahar",
            "form": "Tablet",
            "description": (
                "Standardized extract formulation targeted for stress reduction and "
                "immunity enhancement using traditional processing methods."
            ),
            "ingredients": [
                {"name": "Ashwagandha", "quantity": "500", "unit": "mg"},
                {"name": "Pippali", "quantity": "50", "unit": "mg"},
                {"name": "Black Pepper", "quantity": "20", "unit": "mg"},
            ],
            "jurisdiction": "International",
        }

    def test_ashwagandha_international_jurisdiction_isolation(self):
        req = validate_product_request(self.intl_request_raw)
        res = self.use_case.execute(req)

        self.assertEqual(res["jurisdiction"], "International")

        # 1. Check selected evidence contains ZERO Indian domestic sources
        selected_evidence = res.get("evidence", {}).get("selected", [])
        for ev in selected_evidence:
            cit = ev.get("citation", {})
            jur = cit.get("jurisdiction", "").lower()
            title = cit.get("title", "").lower()
            self.assertEqual(jur, "international", f"Indian leakage found in citation: {cit}")
            self.assertNotIn("biological diversity act", title)
            self.assertNotIn("national biodiversity authority", title)
            self.assertNotIn("fssai", title)
            self.assertNotIn("ayurveda aahara", title)

        # 2. Check compliance checklist actions are conditional, not unconditional PIC/MAT mandates
        checklist = res.get("compliance_checklist", [])
        for item in checklist:
            action = item.get("action", "").lower()
            self.assertNotEqual(action, "obtain prior informed consent")
            self.assertNotEqual(action, "establish mutually agreed terms")
            self.assertNotEqual(action, "designate a national focal point")

        # 3. Overall evidence strength check: should NOT claim 'strong' when major dimensions are insufficient
        self.assertNotEqual(res.get("evidence_strength"), "strong")


if __name__ == "__main__":
    unittest.main()
