import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.product_analysis.domain.product_request import validate_product_request
from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase

sample_payload = {
    "productName": "Ashwagandha Wellness Tablet",
    "category": "Ayurveda-Aahar",
    "form": "Tablet",
    "description": "Standardized extract formulation targeted for stress reduction.",
    "ingredients": [
        {"name": "Ashwagandha", "quantity": "500", "unit": "mg"},
        {"name": "Pipali", "quantity": "50", "unit": "mg"}
    ],
    "jurisdiction": "India"
}

req = validate_product_request(sample_payload)
uc = ProductAnalysisUseCase(base_dir)

dimensions = uc._domain_router.route(req)
targeted_queries = uc._query_builder.build_queries(req, dimensions)
retrieval_uc = uc._make_retrieval_use_case()

# Warmup model/store
_ = retrieval_uc.execute(query="warmup", top_k=1)

# 1. Sequential execution
t0 = time.perf_counter()
seq_results = []
for tq in targeted_queries:
    out = retrieval_uc.execute(
        query=tq.query_text,
        top_k=5,
        jurisdiction=req.jurisdiction,
        domain=tq.legal_domain,
    )
    seq_results.append(out)
t1 = time.perf_counter()
seq_time = t1 - t0
print(f"Sequential retrieval (6 queries): {seq_time:.4f}s", flush=True)

# 2. Parallel execution with ThreadPoolExecutor
def _run_query(tq):
    return retrieval_uc.execute(
        query=tq.query_text,
        top_k=5,
        jurisdiction=req.jurisdiction,
        domain=tq.legal_domain,
    )

t0 = time.perf_counter()
with ThreadPoolExecutor(max_workers=6) as executor:
    par_results = list(executor.map(_run_query, targeted_queries))
t1 = time.perf_counter()
par_time = t1 - t0
print(f"Parallel retrieval (6 queries, ThreadPoolExecutor): {par_time:.4f}s", flush=True)
