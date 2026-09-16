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

# Build prompts
dimensions = uc._domain_router.route(req)
domains_queried = [d.legal_domain for d in dimensions]
targeted_queries = uc._query_builder.build_queries(req, dimensions)

retrieval_uc = uc._make_retrieval_use_case()
all_raw_results = []
chunk_dimension_map = {}

for tq in targeted_queries:
    print(f"Retrieving query: {tq.dimension}", flush=True)
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
    if cid:
        seen_chunk_ids.add(cid)

from src.features.rag.domain.evidence_evaluator import EvidenceEvaluator
combined_assessment = EvidenceEvaluator.evaluate(
    results=deduplicated_results,
    query=f"product analysis {req.product_name}",
    jurisdiction=req.jurisdiction,
    domain=None,
)

retrieval_output_combined = {
    "results": deduplicated_results,
    "evidence_assessment": combined_assessment,
    "jurisdiction_filter": req.jurisdiction,
    "domain_filter": None,
}
full_selection_output = uc._evidence_selector.execute(
    retrieval_output_combined,
    max_evidence=25,
)
all_selected_evidence = full_selection_output.get("evidence", {}).get("selected", [])
llm_evidence = uc._select_llm_evidence(
    all_selected_evidence,
    chunk_dimension_map,
    cap=10,
)
valid_citation_ids = {
    ev.get("citation", {}).get("citation_id", "")
    for ev in llm_evidence
    if ev.get("citation", {}).get("citation_id")
}

from src.features.product_analysis.domain.analysis_prompt import (
    build_product_evidence_block,
    build_product_analysis_prompt,
)
evidence_block = build_product_evidence_block(llm_evidence)
system_prompt, user_prompt = build_product_analysis_prompt(
    req, evidence_block, domains_queried
)

print(f"System prompt length: {len(system_prompt)} chars", flush=True)
print(f"User prompt length: {len(user_prompt)} chars", flush=True)

llm = uc._get_llm()
print(f"Model: {llm.model}", flush=True)

t0 = time.perf_counter()
try:
    raw_answer = llm.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=2000,
        response_format={"type": "json_object"},
        timeout_seconds=45,
    )
    t1 = time.perf_counter()
    print(f"LLM completed in {t1-t0:.2f}s, response length: {len(raw_answer)} chars", flush=True)
    from src.features.product_analysis.application.structured_response_parser import parse_structured_analysis_response
    parsed = parse_structured_analysis_response(raw_answer, valid_citation_ids)
    print("Parsed JSON successfully!", flush=True)
    print(f"Grounded summary length: {len(parsed.get('grounded_summary') or '')}", flush=True)
except Exception as e:
    t1 = time.perf_counter()
    print(f"LLM failed in {t1-t0:.2f}s: {type(e).__name__}: {e}", flush=True)
