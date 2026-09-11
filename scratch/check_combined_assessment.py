import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.product_analysis.domain.product_request import validate_product_request
from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase
from src.features.rag.domain.evidence_evaluator import EvidenceEvaluator

payload = {
    "productName": "Ashwagandha Wellness Tablet",
    "category": "Ayurveda-Aahar",
    "form": "Tablet",
    "description": "Standardized herbal tablet formulation intended for general wellness, using traditional processing methods.",
    "ingredients": [
        {"name": "Ashwagandha (Withania somnifera)", "quantity": "500", "unit": "mg"},
        {"name": "Pippali (Piper longum)", "quantity": "50", "unit": "mg"},
        {"name": "Black Pepper", "quantity": "25", "unit": "mg"}
    ],
    "jurisdiction": "India"
}

req = validate_product_request(payload)
use_case = ProductAnalysisUseCase(base_dir)

dimensions = use_case._domain_router.route(req)
targeted_queries = use_case._query_builder.build_queries(req, dimensions)
retrieval_uc = use_case._make_retrieval_use_case()

all_raw_results = []
chunk_dimension_map = {}

for tq in targeted_queries:
    retrieval_output = retrieval_uc.execute(
        query=tq.query_text,
        top_k=5,
        jurisdiction=req.jurisdiction,
        domain=tq.legal_domain,
    )
    for result in retrieval_output.get("results", []):
        cid = result.get("chunk_id") or ""
        if cid not in chunk_dimension_map:
            chunk_dimension_map[cid] = tq.dimension
        all_raw_results.append(result)

seen_chunk_ids = set()
deduplicated_results = []
for result in all_raw_results:
    cid = result.get("chunk_id") or ""
    if cid and cid in seen_chunk_ids:
        continue
    deduplicated_results.append(result)

print(f"Total deduplicated results: {len(deduplicated_results)}")

combined_assessment = EvidenceEvaluator.evaluate(
    results=deduplicated_results,
    query=f"product analysis {req.product_name}",
    jurisdiction=req.jurisdiction,
    domain=None,
)

print("\nCombined Assessment:")
print(combined_assessment)
