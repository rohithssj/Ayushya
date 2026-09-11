import os
import sys
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

env_local_path = os.path.join(base_dir, ".env.local")
if os.path.exists(env_local_path):
    with open(env_local_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

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
use_case = ProductAnalysisUseCase(base_dir)

# Override complete method to intercept raw answer
original_complete = use_case._get_llm().complete

def intercept_complete(*args, **kwargs):
    ans = original_complete(*args, **kwargs)
    print("\n[INTERCEPT] Raw OpenRouter LLM Response (Length: %d):" % len(ans))
    print(ans)
    return ans

use_case._get_llm().complete = intercept_complete

res = use_case.execute(req, analysis_id="intercept-test")

print("\n[RESULT]")
print("Abstained:", res.get("abstained"))
print("Strength:", res.get("evidence_strength"))
print("Summary Len:", len(res.get("grounded_summary") or ""))
print("Compliance Checklist Count:", len(res.get("compliance_checklist") or []))
print("Compliance Items:")
print(json.dumps(res.get("compliance_checklist"), indent=2))
