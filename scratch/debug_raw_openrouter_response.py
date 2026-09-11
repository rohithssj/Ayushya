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
from src.features.product_analysis.domain.analysis_prompt import build_product_evidence_block, build_product_analysis_prompt
from src.features.product_analysis.application.structured_response_parser import parse_structured_analysis_response

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

full_selection_output = use_case._evidence_selector.execute(
    {"results": deduplicated_results, "jurisdiction_filter": req.jurisdiction, "domain_filter": None, "evidence_assessment": {"strength": "strong", "abstention_recommended": False}},
    max_evidence=25,
)
all_selected_evidence = full_selection_output.get("evidence", {}).get("selected", [])
llm_evidence = use_case._select_llm_evidence(all_selected_evidence, chunk_dimension_map, cap=10)

valid_citation_ids = {
    ev.get("citation", {}).get("citation_id", "")
    for ev in llm_evidence
    if ev.get("citation", {}).get("citation_id")
}

print(f"Valid Citation IDs ({len(valid_citation_ids)}):", list(valid_citation_ids))

evidence_block = build_product_evidence_block(llm_evidence)
system_prompt, user_prompt = build_product_analysis_prompt(req, evidence_block, [d.legal_domain for d in dimensions])

llm = use_case._get_llm()
print("Calling OpenRouter with response_format={'type': 'json_object'}...")

try:
    raw_answer = llm.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )
    print("\n=== RAW OPENROUTER ANSWER ===")
    print(raw_answer)

    parsed = parse_structured_analysis_response(raw_answer, valid_citation_ids)
    print("\n=== PARSED RESULT ===")
    print("parse_fallback:", parsed.get("_parse_fallback"))
    print("fallback_reason:", parsed.get("_fallback_reason"))
    print("grounded_summary present:", bool(parsed.get("grounded_summary")))
    print("compliance_checklist count:", len(parsed.get("compliance_checklist") or []))
    print("compliance_checklist:", json.dumps(parsed.get("compliance_checklist"), indent=2))
except Exception as e:
    print("OpenRouter call failed:", type(e).__name__, str(e))
