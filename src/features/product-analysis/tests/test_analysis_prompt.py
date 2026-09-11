"""
Tests for the analysis prompt builders – ensure they produce non‑empty strings
and include expected placeholders.
"""
import unittest

from src.features.product_analysis.domain.analysis_prompt import (
    build_product_evidence_block,
    build_product_analysis_prompt,
)

class TestAnalysisPromptBuilders(unittest.TestCase):
    """B — Prompt builder unit tests."""

    def test_evidence_block_formats_items(self):
        evidence = [
            {"text": "Clause 1 text", "citation": {"citation_id": "c1"}},
            {"text": "Clause 2 text", "citation": {"citation_id": "c2"}},
        ]
        block = build_product_evidence_block(evidence)
        self.assertIsInstance(block, str)
        self.assertIn("c1", block)
        self.assertIn("Clause 1 text", block)
        self.assertIn("c2", block)
        self.assertIn("Clause 2 text", block)

    def test_analysis_prompt_includes_product_name_and_evidence(self):
        class DummyReq:
            product_name = "Test Product"
            jurisdiction = "india"
            form = "Tablet"
            ingredients = []
            description = "Desc"
            user_selected_classification = "Ayurveda-Aahar"

        req = DummyReq()
        evidence_block = "<evidence>"
        domains = ["ayurveda-aahar", "drugs-cosmetics"]
        system_prompt, user_prompt = build_product_analysis_prompt(req, evidence_block, domains)
        self.assertIn("Test Product", user_prompt)
        self.assertIn("<evidence>", user_prompt)
        self.assertIn("Ayurveda-Aahar", user_prompt)
        self.assertTrue(system_prompt.strip())
        self.assertTrue(user_prompt.strip())

if __name__ == "__main__":
    unittest.main()
