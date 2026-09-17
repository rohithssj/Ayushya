"""
Regression Test Suite — AyurVeda BioShield Canonical Tests
"""

import json
import unittest
from src.features.product_analysis.domain.product_request import validate_product_request

from src.features.product_analysis.domain.domain_router import DomainRouter
from src.features.product_analysis.domain.query_builder import QueryBuilder
from src.features.product_analysis.application.product_analysis_use_case import _build_classification


def _canonical_bioshield_payload(
    user_proposal: str = "No preference — let AYUSHYA assess",
    disease_claim: bool = False,
):
    claims = "Supports immunity, helps the body manage everyday stress, promotes healthy digestion, and supports natural wellness."
    if disease_claim:
        disease_text = "Prevents and helps treat diabetes and arthritis."
    else:
        disease_text = ""

    return {
        "productName": "AyurVeda BioShield",
        "form": "Tablet",
        "intended_use": "Daily wellness product for general immune and stress support.",
        "product_claims": claims,
        "disease_claim_flag": disease_claim,
        "disease_claim_text": disease_text,
        "is_classical_basis": "unknown",
        "classical_reference": "",
        "manufacturing_processing": "Extracts processed and blended into tablets in India.",
        "category": user_proposal,
        "ingredients": [
            {"name": "Ashwagandha (Withania somnifera) root extract", "quantity": "300", "unit": "mg"},
            {"name": "Turmeric (Curcuma longa) rhizome extract", "quantity": "200", "unit": "mg"},
            {"name": "Neem (Azadirachta indica) leaf extract", "quantity": "100", "unit": "mg"},
            {"name": "Pippali (Piper longum) fruit extract", "quantity": "50", "unit": "mg"},
            {"name": "Black pepper (Piper nigrum) extract", "quantity": "25", "unit": "mg"},
        ],
        "jurisdiction": "India",
    }


class TestBioShieldRegression(unittest.TestCase):

    def test_bioshield_no_preference(self):
        """BioShield Test A: No preference hypothesis -> Multi-domain routing."""
        payload = _canonical_bioshield_payload(user_proposal="No preference — let AYUSHYA assess")
        req = validate_product_request(payload)
        self.assertEqual(req.product_name, "AyurVeda BioShield")

        router = DomainRouter()
        dims = router.route(req)
        legal_domains = [d.legal_domain for d in dims]

        self.assertIn("ayurveda-aahar", legal_domains)
        self.assertIn("biodiversity", legal_domains)
        self.assertIn("patents", legal_domains)

    def test_bioshield_ingredient_grounding_no_tulsi(self):
        """Critical Issue 2 & 5: Tulsi must NEVER appear in BioShield outputs or decision signals."""
        payload = _canonical_bioshield_payload()
        req = validate_product_request(payload)
        cls = _build_classification(None, req, "strong")

        cls_dict = cls.to_dict()
        cls_str = str(cls_dict)

        self.assertNotIn("Tulsi", cls_str)
        self.assertNotIn("tulsi", cls_str)

        ingredients_signal = cls.decision_signals.get("ingredients", "")
        self.assertIn("Ashwagandha", ingredients_signal)
        self.assertIn("Turmeric", ingredients_signal)
        self.assertIn("Neem", ingredients_signal)
        self.assertIn("Pippali", ingredients_signal)
        self.assertIn("Black pepper", ingredients_signal)

    def test_bioshield_classical_basis_integrity(self):
        """Critical Issue 3 & 7: is_classical_basis='unknown' must produce proper signal, NOT non-classical=no."""
        payload = _canonical_bioshield_payload()
        req = validate_product_request(payload)
        cls = _build_classification(None, req, "strong")

        classical_signal = cls.decision_signals.get("classical_basis", "")
        self.assertEqual(
            classical_signal,
            "Classical basis could not be independently established because an authoritative formulation reference was not provided."
        )
        self.assertIn("Authoritative classical formulation reference text and recipe source", cls.missing_information)

    def test_bioshield_wellness_vs_disease_claim_variants(self):
        """Critical Issue 4: Variant A (Wellness) vs Variant B (Disease Claim) routing and signals."""
        # Variant A: Wellness Only
        req_a = validate_product_request(_canonical_bioshield_payload(disease_claim=False))
        cls_a = _build_classification(None, req_a, "strong")
        self.assertEqual(cls_a.decision_signals.get("disease_claims"), "None identified.")

        # Variant B: Disease Claim
        req_b = validate_product_request(_canonical_bioshield_payload(disease_claim=True))
        cls_b = _build_classification(None, req_b, "strong")
        self.assertIn("Prevents and helps treat diabetes and arthritis.", cls_b.decision_signals.get("disease_claims", ""))

        # Check domain routing differs / surfaces drugs-cosmetics sensitivity for disease claim
        domains_b = [d.legal_domain for d in DomainRouter().route(req_b)]
        self.assertIn("drugs-cosmetics", domains_b)

    def test_bioshield_hypothesis_isolation(self):
        """Critical Issue 8 & 9: User proposal remains hypothesis across A, B, C, D proposals."""
        for proposal in [
            "No preference — let AYUSHYA assess",
            "Ayurveda-Aahar",
            "Proprietary Ayurvedic Formulation",
            "Classical Ayurvedic Formulation",
        ]:
            req = validate_product_request(_canonical_bioshield_payload(user_proposal=proposal))
            cls = _build_classification(None, req, "strong")

            expected_user_selected = (
                "No preference — let AYUSHYA assess"
                if proposal == "No preference — let AYUSHYA assess"
                else proposal
            )
            self.assertEqual(cls.user_selected, expected_user_selected)
            self.assertTrue(cls.requires_verification)

    def test_bioshield_international_jurisdiction(self):
        """Fresh International BioShield test: destination target country unstated -> category undetermined."""
        payload = _canonical_bioshield_payload()
        payload["jurisdiction"] = "International"
        req = validate_product_request(payload)

        router = DomainRouter()
        dims = router.route(req)
        legal_domains = [d.legal_domain for d in dims]
        self.assertIn("treaties", legal_domains)
        self.assertIn("cbd", legal_domains)

        cls = _build_classification(None, req, "strong")
        self.assertIn("Undetermined (Destination Target Country Not Specified)", cls.primary.get("category", ""))
        self.assertEqual(cls.primary.get("status"), "not_established")
        self.assertIn("Destination target country for import and market authorization", cls.missing_information)


    def test_bioshield_audit_regression_constraints(self):
        """BioShield Audit Regression: Covers evidence, wording, and citation integrity constraints."""
        from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase
        payload = _canonical_bioshield_payload()
        req = validate_product_request(payload)
        use_case = ProductAnalysisUseCase(base_dir=".")
        class MockLLMProvider:
            def complete(self, system_prompt="", user_prompt="", **kwargs):
                return json.dumps({
                    "grounded_summary": "Preliminary analysis based on supplied evidence for AyurVeda BioShield.",
                    "classification": {
                        "user_selected": "No preference — let AYUSHYA assess",
                        "preliminary_assessment": "Potentially subject to evaluation under FSSAI Food Safety and Standards (Ayurveda Aahara) Regulations, 2022, subject to verification.",
                        "evidence_strength": "strong",
                        "supporting_citation_ids": [],
                        "primary": {
                            "category": "Ayurveda Aahar",
                            "status": "potentially_applicable",
                            "evidence_strength": "strong",
                            "reasoning": "Product formulated using botanical extracts."
                        }
                    },
                    "ip_assessment": [
                        {
                            "ip_type": "Patent",
                            "relevance": "potentially_relevant",
                            "preliminary_assessment": "Formulation patent protection limited by Section 3(p)/3(e), but novel extraction processes may be patentable.",
                            "reasoning": "Extract mixture assessment.",
                            "evidence_strength": "strong",
                            "supporting_citation_ids": []
                        }
                    ],
                    "regulatory_assessment": [
                        {
                            "framework": "Ayurveda-Aahar",
                            "why_applicable": "Complies with Ayurveda Aahara guidance.",
                            "relevant_provisions": ["Clause 3"],
                            "evidence_strength": "strong",
                            "supporting_citation_ids": []
                        }
                    ],
                    "tk_biodiversity": {
                        "tk_considerations": "Biological resources utilized.",
                        "biodiversity_considerations": "Biological Diversity Act ABS requirements.",
                        "abs_note": "Requires verification with NBA.",
                        "evidence_strength": "strong",
                        "supporting_citation_ids": [],
                        "insufficient": False
                    },
                    "compliance_checklist": [
                        {
                            "action": "Submit NBA access notification for biological resource utilization.",
                            "reason": "Indian biological resources used in formulation.",
                            "legal_area": "Biodiversity / ABS",
                            "priority": "high",
                            "supporting_citation_id": None
                        }
                    ]
                })

        use_case._llm = MockLLMProvider()
        result = use_case.execute(req)






        # 1. Classical-basis unknown remains unknown / preliminary
        self.assertEqual(payload["is_classical_basis"], "unknown")
        self.assertEqual(result["classification"]["user_selected"], "No preference — let AYUSHYA assess")


        # 2. Check wording: no 'falling under' and no 'using traditional methods'
        structured_fields = {
            "classification": result.get("classification"),
            "ip_assessment": result.get("ip_assessment"),
            "regulatory_assessment": result.get("regulatory_assessment"),
            "tk_biodiversity": result.get("tk_biodiversity"),
            "compliance_checklist": result.get("compliance_checklist"),
        }
        struct_str = str(structured_fields).lower()
        self.assertNotIn("falling under", struct_str)
        self.assertNotIn("using traditional methods", struct_str)



        # 3. Verify Biodiversity/TK evidence
        tk_bio = result.get("tk_biodiversity", {})
        self.assertIsNotNone(tk_bio)
        self.assertFalse(tk_bio.get("insufficient", True))

        # 4. Verify IP evidence
        ip_res = result.get("ip_assessment", [])
        self.assertTrue(len(ip_res) > 0)
        self.assertEqual(ip_res[0].get("ip_type"), "Patent")

        # 5. Verify Regulatory and Compliance evidence
        reg_res = result.get("regulatory_assessment", [])
        self.assertTrue(len(reg_res) > 0)

        comp_res = result.get("compliance_checklist", [])
        self.assertTrue(len(comp_res) > 0)

        # 6. Check citation integrity across all dimensions: every citation ID must exist in evidence citations
        valid_citations = {ev["citation"]["citation_id"] for ev in result.get("evidence", {}).get("selected", []) if "citation" in ev and "citation_id" in ev["citation"]}
        self.assertTrue(len(valid_citations) > 0)



        def check_citations(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in ("supporting_citation_ids", "supporting_citation_id"):
                        cids = v if isinstance(v, list) else ([v] if v else [])
                        for cid in cids:
                            if cid:
                                self.assertIn(cid, valid_citations, f"Fabricated or invalid citation ID found: {cid}")
                    else:
                        check_citations(v)
            elif isinstance(obj, list):
                for elem in obj:
                    check_citations(elem)

        check_citations(result)




if __name__ == "__main__":
    unittest.main()

