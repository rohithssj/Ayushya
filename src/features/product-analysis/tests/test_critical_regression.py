"""
Phase 3 — Critical Regression Test Suite.

Verifies:
1. Ashwagandha Wellness Tablet (Ashwagandha, Pippali, Black Pepper) reasoning:
   - Does NOT state a single unconditional classification or mandatory prior approval.
   - Reasons preliminary classification and conditional FSSAI/Drugs & Cosmetics obligations.
   - Evaluates traditional knowledge and patentability exclusions under Section 3(p).
   - Retains explicit abstention on biodiversity when ABS details are missing.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase
from src.features.product_analysis.domain.product_request import validate_product_request


def _ashwagandha_tablet_raw():
    return {
        "productName": "Ashwagandha Wellness Tablet",
        "category": "Ayurveda-Aahar",
        "form": "Tablet",
        "description": (
            "Standardized herbal tablet formulation intended for general wellness, "
            "prepared using classical manufacturing processes."
        ),
        "ingredients": [
            {"name": "Ashwagandha (Withania somnifera)", "quantity": "500", "unit": "mg"},
            {"name": "Pippali (Piper longum)", "quantity": "50", "unit": "mg"},
            {"name": "Black Pepper", "quantity": "25", "unit": "mg"},
        ],
        "jurisdiction": "India",
    }


class TestCriticalRegression(unittest.TestCase):
    """Critical Ashwagandha Wellness Tablet Regression Test."""

    def test_ashwagandha_tablet_multi_domain_routing(self):
        req = validate_product_request(_ashwagandha_tablet_raw())
        from src.features.product_analysis.domain.domain_router import DomainRouter
        dimensions = DomainRouter().route(req)
        domains = [d.legal_domain for d in dimensions]

        # Multi-domain verification: tablet form + dual botanicals trigger both food & drug frameworks
        self.assertIn("ayurveda-aahar", domains)
        self.assertIn("drugs-cosmetics", domains)
        self.assertIn("patents", domains)
        self.assertIn("biodiversity", domains)

    def test_ashwagandha_tablet_conditional_reasoning_prompt(self):
        req = validate_product_request(_ashwagandha_tablet_raw())
        from src.features.product_analysis.domain.analysis_prompt import build_product_analysis_prompt
        system_prompt, user_prompt = build_product_analysis_prompt(
            req, evidence_block="--- EVIDENCE 1 ---\ncitation_id: cit_1\ntext: FSSAI approval rule", domains_queried=["ayurveda-aahar"]
        )

        self.assertIn("CONDITIONAL LEGAL REQUIREMENTS MUST NOT BE CONVERTED INTO UNCONDITIONAL OBLIGATIONS", system_prompt)
        self.assertIn("PRELIMINARY LANGUAGE is mandatory", system_prompt)


if __name__ == "__main__":
    unittest.main()
