import os
import sys
import time
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

dotenv_path = os.path.join(base_dir, ".env.local")
if os.path.exists(dotenv_path):
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

from src.features.product_analysis.domain.product_request import validate_product_request
from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase
from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase

pa_payloads = [
    {
        "productName": "Ashwagandha Wellness Tablet",
        "category": "Ayurveda-Aahar",
        "form": "Tablet",
        "description": "Standardized extract formulation targeted for stress reduction.",
        "ingredients": [
            {"name": "Ashwagandha", "quantity": "500", "unit": "mg"},
            {"name": "Pipali", "quantity": "50", "unit": "mg"}
        ],
        "jurisdiction": "India"
    },
    {
        "productName": "Triphala Digestive Churna",
        "category": "Classical Formulation",
        "form": "Syrup / Churna",
        "description": "Classical Ayurvedic formulation of Haritaki, Bibhitaki, and Amalaki.",
        "ingredients": [
            {"name": "Haritaki", "quantity": "333", "unit": "mg"},
            {"name": "Bibhitaki", "quantity": "333", "unit": "mg"},
            {"name": "Amalaki", "quantity": "334", "unit": "mg"}
        ],
        "jurisdiction": "India"
    },
    {
        "productName": "Curcumin Joint Health Capsule",
        "category": "Phytopharmaceutical",
        "form": "Capsule",
        "description": "95% standardized Curcuminoid extract with Piperine for joint support.",
        "ingredients": [
            {"name": "Curcumin extract", "quantity": "250", "unit": "mg"},
            {"name": "Piperine", "quantity": "5", "unit": "mg"}
        ],
        "jurisdiction": "India"
    }
]

chat_queries = [
    {"query": "Can I patent an herbal mixture under Indian law?", "jurisdiction": "India"},
    {"query": "What are the labelling requirements for Ayurveda-Aahar products under FSSAI?", "jurisdiction": "India"},
    {"query": "What is the procedure for registering a non-traditional trademark in India?", "jurisdiction": "India"}
]

print("=== MANDATORY BENCHMARK RUN (AFTER OPTIMIZATIONS) ===", flush=True)

pa_use_case = ProductAnalysisUseCase(base_dir)
pa_results = []

for i, payload in enumerate(pa_payloads, 1):
    req = validate_product_request(payload)
    t0 = time.perf_counter()
    res = pa_use_case.execute(req, analysis_id=f"bench_pa_{i}")
    t1 = time.perf_counter()
    total_t = t1 - t0
    cits = res.get("citations", [])
    grounded_summary = res.get("grounded_summary") or ""
    status = 200 if grounded_summary or res.get("abstained") else 500
    pa_results.append({
        "name": f"Product #{i}",
        "total_s": round(total_t, 2),
        "status": status,
        "citations_count": len(cits),
        "abstained": res.get("abstained", False)
    })
    print(f"Product #{i} complete: {total_t:.2f}s | HTTP {status} | Citations: {len(cits)}", flush=True)

chat_use_case = GroundedAnswerUseCase(base_dir)
chat_results = []

for i, q in enumerate(chat_queries, 1):
    t0 = time.perf_counter()
    res = chat_use_case.execute(
        query=q["query"],
        jurisdiction=q["jurisdiction"],
        top_k=5,
        request_id=f"bench_chat_{i}"
    )
    t1 = time.perf_counter()
    total_t = t1 - t0
    cits = res.get("citations", [])
    answer = res.get("answer") or ""
    status = 200 if answer or res.get("abstained") else 500
    chat_results.append({
        "name": f"Chat #{i}",
        "total_s": round(total_t, 2),
        "status": status,
        "citations_count": len(cits),
        "abstained": res.get("abstained", False)
    })
    print(f"Chat #{i} complete: {total_t:.2f}s | HTTP {status} | Citations: {len(cits)}", flush=True)

print("\nSUMMARY_TABLE_START", flush=True)
print(json.dumps({"product": pa_results, "chat": chat_results}, indent=2), flush=True)
print("SUMMARY_TABLE_END", flush=True)
