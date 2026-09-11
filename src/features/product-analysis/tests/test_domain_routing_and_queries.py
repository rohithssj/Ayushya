import unittest

from src.features.product_analysis.domain.domain_router import DomainRouter
from src.features.product_analysis.domain.query_builder import QueryBuilder
from src.features.product_analysis.domain.product_request import validate_product_request


def _raw(**overrides):
    data = {
        "productName": "Ashwagandha Wellness Tablet",
        "category": "Ayurveda-Aahar",
        "form": "Tablet",
        "description": (
            "Standardized herbal tablet formulation intended for general wellness, "
            "using traditional processing methods."
        ),
        "ingredients": [
            {"name": "Ashwagandha (Withania somnifera)", "quantity": "500", "unit": "mg"},
            {"name": "Pippali (Piper longum)", "quantity": "50", "unit": "mg"},
        ],
        "jurisdiction": "India",
    }
    data.update(overrides)
    return data


class TestDomainRoutingAndQueries(unittest.TestCase):
    def test_ayurveda_aahar_routes_to_relevant_domains_only(self):
        request = validate_product_request(_raw())
        dimensions = DomainRouter().route(request)
        domains = [d.legal_domain for d in dimensions]

        self.assertIn("ayurveda-aahar", domains)
        self.assertIn("patents", domains)
        self.assertIn("biodiversity", domains)
        self.assertIn("trademarks", domains)
        self.assertNotIn("drugs-cosmetics", domains)
        self.assertNotIn("treaties", domains)

    def test_international_request_adds_treaty_and_cbd_domains(self):
        request = validate_product_request(_raw(jurisdiction="International"))
        domains = [d.legal_domain for d in DomainRouter().route(request)]

        self.assertIn("treaties", domains)
        self.assertIn("cbd", domains)

    def test_visual_and_label_signals_route_design_and_copyright(self):
        request = validate_product_request(
            _raw(description="Distinctive bottle shape, label artwork, and packaging copy.")
        )
        domains = [d.legal_domain for d in DomainRouter().route(request)]

        self.assertIn("designs", domains)
        self.assertIn("copyright", domains)

    def test_query_builder_creates_targeted_product_specific_queries(self):
        request = validate_product_request(_raw())
        dimensions = DomainRouter().route(request)
        queries = QueryBuilder().build_queries(request, dimensions)

        self.assertEqual(len(queries), len(dimensions))
        self.assertTrue(any(q.dimension == "product_classification" for q in queries))
        self.assertTrue(any(q.legal_domain == "patents" for q in queries))
        self.assertTrue(all(q.jurisdiction == "India" for q in queries))
        self.assertTrue(any("Ashwagandha" in q.query_text for q in queries))


if __name__ == "__main__":
    unittest.main()
