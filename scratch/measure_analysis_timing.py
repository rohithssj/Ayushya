import time
import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

def run_timing_test():
    print("=== STARTING PRODUCT ANALYSIS TIMING MEASUREMENT ===")
    t0 = time.perf_counter()

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

    t1 = time.perf_counter()
    print(f"Imports + Setup: {(t1 - t0)*1000:.2f} ms")

    req = validate_product_request(payload)
    use_case = ProductAnalysisUseCase(base_dir)

    t2 = time.perf_counter()
    print(f"Init UseCase: {(t2 - t1)*1000:.2f} ms")

    res = use_case.execute(req, analysis_id="test-timing-1")
    t3 = time.perf_counter()

    print(f"Total Execution Time: {(t3 - t0)*1000:.2f} ms")
    print(f"Abstained: {res.get('abstained')}")
    print(f"Evidence Strength: {res.get('evidence_strength')}")
    print(f"Compliance Items Count: {len(res.get('compliance_checklist', []))}")
    print("Compliance Items:")
    print(json.dumps(res.get("compliance_checklist", []), indent=2))

if __name__ == "__main__":
    run_timing_test()
