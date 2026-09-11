import time
import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.product_analysis.domain.product_request import validate_product_request
from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase
from src.features.product_analysis.domain.domain_router import DomainRouter
from src.features.product_analysis.domain.query_builder import QueryBuilder
from src.features.rag.application.hybrid_retrieval_use_case import HybridRetrievalUseCase

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
router = DomainRouter()
dims = router.route(req)
print("=== 1. ROUTED DIMENSIONS ===")
for d in dims:
    print(f"Dimension: {d.dimension} | Domain: {d.legal_domain} | Reason: {d.why_relevant}")

builder = QueryBuilder()
queries = builder.build_queries(req, dims)
print("\n=== 2. TARGETED QUERIES ===")
for q in queries:
    print(f"Dim: {q.dimension} | Domain: {q.legal_domain} | Query: {q.query_text}")

retrieval_uc = HybridRetrievalUseCase(base_dir)
all_results = []
chunk_dim_map = {}
for q in queries:
    res = retrieval_uc.execute(query=q.query_text, top_k=5, jurisdiction=req.jurisdiction, domain=q.legal_domain)
    chunks = res.get("results", [])
    print(f"\nQuery '{q.dimension}' returned {len(chunks)} chunks:")
    for c in chunks:
        cid = c.get("chunk_id")
        title = c.get("title")
        section = c.get("section")
        print(f"  - [{cid}] {title} section={section}")
        if cid not in chunk_dim_map:
            chunk_dim_map[cid] = q.dimension
        all_results.append(c)

print(f"\n=== 3. TOTAL CANDIDATE CHUNKS: {len(all_results)} ===")

use_case = ProductAnalysisUseCase(base_dir)
res = use_case.execute(req, analysis_id="diag-compliance-1")

print("\n=== 4. LLM RAW AND PARSED COMPLIANCE CHECKLIST ===")
print("Compliance items in result:", json.dumps(res.get("compliance_checklist"), indent=2))
