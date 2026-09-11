"""
Tests — ProductAnalysisRequest validation.

Covers: required fields, max lengths, ingredient structure, quantity/unit
validity, supported jurisdiction, supported classification values, and
prompt injection protection.
"""
# sys.path fixup — ensures project root is on sys.path when running via
# `unittest discover -s src/features/product-analysis/tests` without -t
import sys as _sys, os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))))
if _ROOT not in _sys.path:
    _sys.path.insert(0, _ROOT)

import unittest

from src.features.product_analysis.domain.product_request import (
    ProductAnalysisRequest,
    ProductRequestValidationError,
    validate_product_request,
    MAX_PRODUCT_NAME_LEN,
    MAX_DESCRIPTION_LEN,
    MAX_INGREDIENTS,
)


def _valid_raw() -> dict:
    return {
        "productName": "Ashwagandha Wellness Tablet",
        "category": "Ayurveda-Aahar",
        "form": "Tablet",
        "description": "Standardized herbal tablet using traditional processing methods.",
        "ingredients": [
            {"name": "Ashwagandha (Withania somnifera)", "quantity": "500", "unit": "mg"},
            {"name": "Pippali (Piper longum)", "quantity": "50", "unit": "mg"},
            {"name": "Black Pepper", "quantity": "25", "unit": "mg"},
        ],
        "jurisdiction": "India",
    }


class TestProductRequestValidation(unittest.TestCase):
    """A — Product request validation tests."""

    # ── Required fields ────────────────────────────────────────────────────

    def test_valid_request_succeeds(self):
        req = validate_product_request(_valid_raw())
        self.assertIsInstance(req, ProductAnalysisRequest)
        self.assertEqual(req.product_name, "Ashwagandha Wellness Tablet")
        self.assertEqual(req.jurisdiction, "India")
        self.assertEqual(len(req.ingredients), 3)

    def test_missing_product_name_raises(self):
        raw = _valid_raw()
        del raw["productName"]
        with self.assertRaises(ProductRequestValidationError) as ctx:
            validate_product_request(raw)
        self.assertIn("productName", str(ctx.exception))

    def test_empty_product_name_raises(self):
        raw = _valid_raw()
        raw["productName"] = "   "
        with self.assertRaises(ProductRequestValidationError):
            validate_product_request(raw)

    def test_missing_description_raises(self):
        raw = _valid_raw()
        del raw["description"]
        with self.assertRaises(ProductRequestValidationError) as ctx:
            validate_product_request(raw)
        self.assertIn("description", str(ctx.exception))

    def test_missing_jurisdiction_raises(self):
        raw = _valid_raw()
        del raw["jurisdiction"]
        with self.assertRaises(ProductRequestValidationError):
            validate_product_request(raw)

    # ── Length limits ──────────────────────────────────────────────────────

    def test_product_name_too_long_raises(self):
        raw = _valid_raw()
        raw["productName"] = "A" * (MAX_PRODUCT_NAME_LEN + 1)
        with self.assertRaises(ProductRequestValidationError) as ctx:
            validate_product_request(raw)
        self.assertIn("productName", str(ctx.exception))

    def test_description_too_long_raises(self):
        raw = _valid_raw()
        raw["description"] = "X" * (MAX_DESCRIPTION_LEN + 1)
        with self.assertRaises(ProductRequestValidationError):
            validate_product_request(raw)

    def test_product_name_at_max_length_succeeds(self):
        raw = _valid_raw()
        raw["productName"] = "A" * MAX_PRODUCT_NAME_LEN
        req = validate_product_request(raw)
        self.assertEqual(len(req.product_name), MAX_PRODUCT_NAME_LEN)

    # ── Jurisdiction validation ────────────────────────────────────────────

    def test_india_jurisdiction_normalised(self):
        raw = _valid_raw()
        raw["jurisdiction"] = "India"
        req = validate_product_request(raw)
        self.assertEqual(req.jurisdiction, "India")

    def test_international_jurisdiction_normalised(self):
        raw = _valid_raw()
        raw["jurisdiction"] = "International"
        req = validate_product_request(raw)
        self.assertEqual(req.jurisdiction, "International")

    def test_invalid_jurisdiction_raises(self):
        raw = _valid_raw()
        raw["jurisdiction"] = "USA"
        with self.assertRaises(ProductRequestValidationError) as ctx:
            validate_product_request(raw)
        self.assertIn("jurisdiction", str(ctx.exception))

    # ── Classification validation ──────────────────────────────────────────

    def test_unknown_classification_defaults_to_other(self):
        raw = _valid_raw()
        raw["category"] = "something-unknown-xyz"
        req = validate_product_request(raw)
        self.assertEqual(req.user_selected_classification, "other")

    def test_valid_classification_preserved(self):
        raw = _valid_raw()
        raw["category"] = "Ayurveda-Aahar"
        req = validate_product_request(raw)
        self.assertEqual(req.user_selected_classification, "Ayurveda-Aahar")

    def test_missing_category_defaults_to_other(self):
        raw = _valid_raw()
        del raw["category"]
        req = validate_product_request(raw)
        self.assertEqual(req.user_selected_classification, "other")

    # ── Ingredient structure validation ────────────────────────────────────

    def test_empty_ingredient_name_raises(self):
        raw = _valid_raw()
        raw["ingredients"] = [{"name": "", "quantity": "100", "unit": "mg"}]
        with self.assertRaises(ProductRequestValidationError):
            validate_product_request(raw)

    def test_non_list_ingredients_raises(self):
        raw = _valid_raw()
        raw["ingredients"] = "not a list"
        with self.assertRaises(ProductRequestValidationError):
            validate_product_request(raw)

    def test_too_many_ingredients_raises(self):
        raw = _valid_raw()
        raw["ingredients"] = [
            {"name": f"Herb{i}", "quantity": "100", "unit": "mg"}
            for i in range(MAX_INGREDIENTS + 1)
        ]
        with self.assertRaises(ProductRequestValidationError):
            validate_product_request(raw)

    def test_ingredient_with_valid_data_accepted(self):
        raw = _valid_raw()
        req = validate_product_request(raw)
        self.assertEqual(req.ingredients[0].name, "Ashwagandha (Withania somnifera)")
        self.assertEqual(req.ingredients[0].quantity, "500")
        self.assertEqual(req.ingredients[0].unit, "mg")

    def test_empty_ingredients_list_accepted(self):
        raw = _valid_raw()
        raw["ingredients"] = []
        req = validate_product_request(raw)
        self.assertEqual(req.ingredients, [])

    # ── Optional traditional knowledge reference ───────────────────────────

    def test_tk_ref_accepted_when_provided(self):
        raw = _valid_raw()
        raw["traditional_knowledge_ref"] = "Referenced in Charaka Samhita, Chikitsa Sthana"
        req = validate_product_request(raw)
        self.assertEqual(req.traditional_knowledge_ref, "Referenced in Charaka Samhita, Chikitsa Sthana")

    def test_tk_ref_none_when_not_provided(self):
        req = validate_product_request(_valid_raw())
        self.assertIsNone(req.traditional_knowledge_ref)

    # ── Prompt injection protection ────────────────────────────────────────

    def test_prompt_injection_in_name_accepted_but_length_limited(self):
        # We don't block content; we limit length to prevent large payloads
        raw = _valid_raw()
        raw["productName"] = "Test\nIgnore previous\nPretend you are"  # injection attempt
        req = validate_product_request(raw)
        # Should succeed but the name is short enough — the LLM prompt
        # is constructed in the use case, not here; the system prompt enforces behavior
        self.assertTrue(len(req.product_name) <= MAX_PRODUCT_NAME_LEN)

    def test_very_long_ingredient_name_raises(self):
        raw = _valid_raw()
        raw["ingredients"] = [{"name": "A" * 201, "quantity": "100", "unit": "mg"}]
        with self.assertRaises(ProductRequestValidationError):
            validate_product_request(raw)


if __name__ == "__main__":
    unittest.main()
