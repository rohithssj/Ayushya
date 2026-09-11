import time
import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Read .env.local manually to ensure OPENROUTER_API_KEY is available
env_local_path = os.path.join(base_dir, ".env.local")
if os.path.exists(env_local_path):
    with open(env_local_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

def run_real_e2e_test():
    print("=== STARTING REAL E2E PRODUCT ANALYSIS TEST ===")
    t_start = time.perf_counter()

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

    t_validate_0 = time.perf_counter()
    req = validate_product_request(payload)
    use_case = ProductAnalysisUseCase(base_dir)
    t_validate_1 = time.perf_counter()
    print(f"Validation & Setup: {(t_validate_1 - t_validate_0)*1000:.2f} ms")

    t_exec_0 = time.perf_counter()
    res = use_case.execute(req, analysis_id="e2e-verification-ashwagandha")
    t_exec_1 = time.perf_counter()
    t_total = time.perf_counter()

    print(f"\n=== TIMING BREAKDOWN ===")
    print(f"Product Analysis Execution: {(t_exec_1 - t_exec_0)*1000:.2f} ms ({(t_exec_1 - t_exec_0):.2f} s)")
    print(f"Total E2E Pipeline Time: {(t_total - t_start)*1000:.2f} ms ({(t_total - t_start):.2f} s)")

    print(f"\n=== ANALYSIS METRICS ===")
    print(f"Analysis ID: {res.get('analysis_id')}")
    print(f"Abstained: {res.get('abstained')}")
    print(f"Evidence Strength: {res.get('evidence_strength')}")
    print(f"Requires Human Review: {res.get('requires_human_review')}")
    print(f"Citations Count: {len(res.get('citations', []))}")
    print(f"Citations: {res.get('citations')}")

    print(f"\n=== COMPLIANCE CHECKLIST ({len(res.get('compliance_checklist', []))} items) ===")
    print(json.dumps(res.get("compliance_checklist", []), indent=2))

    print(f"\n=== GROUNDED SUMMARY (First 300 chars) ===")
    summary = res.get("grounded_summary") or ""
    print(summary[:300] + ("..." if len(summary) > 300 else ""))

if __name__ == "__main__":
    run_real_e2e_test()
