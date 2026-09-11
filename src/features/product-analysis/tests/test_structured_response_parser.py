import json
import unittest

from src.features.product_analysis.application.structured_response_parser import (
    parse_structured_analysis_response,
)


VALID_IDS = {"cit_patent", "cit_regulation", "cit_biodiversity"}


def _valid_response():
    return {
        "grounded_summary": "This preliminary summary is grounded in the supplied evidence.",
        "classification": {
            "user_selected": "Ayurveda-Aahar",
            "preliminary_assessment": "The supplied evidence supports a preliminary assessment.",
            "evidence_strength": "moderate",
            "supporting_citation_ids": ["cit_regulation"],
        },
        "ip_assessment": [
            {
                "ip_type": "Patent",
                "relevance": "potentially_relevant",
                "preliminary_assessment": "Potentially relevant based on supplied evidence.",
                "reasoning": "The evidence discusses patent eligibility.",
                "evidence_strength": "moderate",
                "supporting_citation_ids": ["cit_patent"],
            }
        ],
        "regulatory_assessment": [
            {
                "framework": "Ayurveda-Aahar framework",
                "why_applicable": "The evidence describes this framework.",
                "relevant_provisions": ["Provision in supplied evidence"],
                "evidence_strength": "moderate",
                "supporting_citation_ids": ["cit_regulation"],
            }
        ],
        "tk_biodiversity": {
            "tk_considerations": "The evidence identifies a possible TK consideration.",
            "biodiversity_considerations": "The evidence identifies a possible biodiversity consideration.",
            "abs_note": "The evidence contains an ABS note.",
            "evidence_strength": "weak",
            "supporting_citation_ids": ["cit_biodiversity"],
            "insufficient": False,
        },
        "compliance_checklist": [
            {
                "action": "Review the supplied regulatory provision.",
                "reason": "The supplied evidence identifies this review step.",
                "legal_area": "Regulatory",
                "priority": "medium",
                "supporting_citation_id": "cit_regulation",
            }
        ],
    }


class TestStructuredResponseParser(unittest.TestCase):
    def test_valid_structured_json_preserves_supported_fields(self):
        result = parse_structured_analysis_response(
            json.dumps(_valid_response()), VALID_IDS
        )
        self.assertFalse(result["_parse_fallback"])
        self.assertEqual(result["classification"]["supporting_citation_ids"], ["cit_regulation"])
        self.assertTrue(result["classification"]["requires_verification"])
        self.assertTrue(result["ip_assessment"][0]["requires_verification"])
        self.assertTrue(result["regulatory_assessment"][0]["requires_verification"])
        self.assertTrue(result["tk_biodiversity"]["requires_verification"])
        self.assertTrue(result["compliance_checklist"][0]["requires_verification"])
        self.assertEqual(result["compliance_checklist"][0]["supporting_citation_id"], "cit_regulation")

    def test_markdown_fenced_json_is_parsed(self):
        result = parse_structured_analysis_response(
            "```json\n" + json.dumps(_valid_response()) + "\n```", VALID_IDS
        )
        self.assertFalse(result["_parse_fallback"])
        self.assertEqual(len(result["ip_assessment"]), 1)

    def test_malformed_json_falls_back_without_summary_or_claims(self):
        result = parse_structured_analysis_response(
            "This is not valid JSON and must not become a legal answer.", VALID_IDS
        )
        self.assertTrue(result["_parse_fallback"])
        self.assertIsNone(result["grounded_summary"])
        self.assertEqual(result["ip_assessment"], [])
        self.assertEqual(result["citations"] if "citations" in result else [], [])

    def test_missing_fields_are_safe(self):
        result = parse_structured_analysis_response(
            json.dumps({"grounded_summary": "A sufficiently long but incomplete summary from the model."}),
            VALID_IDS,
        )
        self.assertIsNone(result["classification"])
        self.assertIsNone(result["tk_biodiversity"])
        self.assertEqual(result["compliance_checklist"], [])

    def test_invalid_enum_values_become_insufficient(self):
        result = parse_structured_analysis_response(
            json.dumps({
                "classification": {
                    "user_selected": "Ayurveda-Aahar",
                    "preliminary_assessment": "Insufficient evidence.",
                    "evidence_strength": "certain",
                    "supporting_citation_ids": [],
                }
            }),
            VALID_IDS,
        )
        self.assertEqual(result["classification"]["evidence_strength"], "insufficient")

    def test_invalid_citation_ids_are_removed(self):
        payload = _valid_response()
        payload["classification"]["supporting_citation_ids"] = ["cit_fake", "cit_regulation"]
        payload["ip_assessment"][0]["supporting_citation_ids"] = ["cit_fake"]
        result = parse_structured_analysis_response(json.dumps(payload), VALID_IDS)
        self.assertEqual(result["classification"]["supporting_citation_ids"], ["cit_regulation"])
        self.assertEqual(result["ip_assessment"], [])

    def test_unsupported_positive_assessments_are_removed(self):
        payload = _valid_response()
        payload["regulatory_assessment"][0]["supporting_citation_ids"] = []
        payload["regulatory_assessment"][0]["evidence_strength"] = "strong"
        result = parse_structured_analysis_response(json.dumps(payload), VALID_IDS)
        self.assertEqual(result["regulatory_assessment"], [])

    def test_insufficient_biodiversity_is_preserved(self):
        result = parse_structured_analysis_response(
            json.dumps({
                "tk_biodiversity": {
                    "evidence_strength": "insufficient",
                    "insufficient": True,
                    "supporting_citation_ids": [],
                }
            }),
            VALID_IDS,
        )
        self.assertTrue(result["tk_biodiversity"]["insufficient"])
        self.assertEqual(result["tk_biodiversity"]["supporting_citation_ids"], [])

    def test_compliance_without_valid_citation_is_removed(self):
        payload = _valid_response()
        payload["compliance_checklist"][0]["supporting_citation_id"] = "cit_fake"
        result = parse_structured_analysis_response(json.dumps(payload), VALID_IDS)
        self.assertEqual(result["compliance_checklist"], [])


if __name__ == "__main__":
    unittest.main()
