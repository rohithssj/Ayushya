import time
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

def run_test():
    print("=== TESTING RETRIEVAL SPEED ===")
    from src.features.product_analysis.domain.product_request import validate_product_request
    from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase

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
    
    t0 = time.perf_counter()
    use_case = ProductAnalysisUseCase(base_dir)
    t1 = time.perf_counter()
    print(f"UseCase init: {(t1 - t0)*1000:.2f} ms")

    dimensions = use_case._domain_router.route(req)
    targeted_queries = use_case._query_builder.build_queries(req, dimensions)
    retrieval_uc = use_case._make_retrieval_use_case()

    t2 = time.perf_counter()
    for q in targeted_queries:
        t_q0 = time.perf_counter()
        res = retrieval_uc.execute(query=q.query_text, top_k=5, jurisdiction=req.jurisdiction, domain=q.legal_domain)
        t_q1 = time.perf_counter()
        print(f"Query '{q.dimension}' ({q.legal_domain}): {(t_q1 - t_q0)*1000:.2f} ms")

    t3 = time.perf_counter()
    print(f"Total Retrieval Time for {len(targeted_queries)} queries: {(t3 - t2)*1000:.2f} ms")

if __name__ == "__main__":
    run_test()
