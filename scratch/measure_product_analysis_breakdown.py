import os
import sys
import time
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Read .env.local manually if env vars not present
dotenv_path = os.path.join(base_dir, ".env.local")
if os.path.exists(dotenv_path):
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

t0 = time.perf_counter()

from src.features.product_analysis.domain.product_request import validate_product_request
from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase
from src.features.rag.infrastructure.openrouter_provider import OpenRouterProvider
from src.features.rag.application.hybrid_retrieval_use_case import HybridRetrievalUseCase
from src.features.rag.domain.evidence_evaluator import EvidenceEvaluator
from src.features.rag.application.evidence_selection_use_case import EvidenceSelectionUseCase
from src.features.product_analysis.application.structured_response_parser import parse_structured_analysis_response

t_imports = time.perf_counter()

# Instrument ProductAnalysisUseCase execution
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

print(f"Python import time: {t_imports - t0:.4f}s", flush=True)

# Let's run and instrument ProductAnalysisUseCase step by step
uc = ProductAnalysisUseCase(base_dir)

t_init = time.perf_counter()
print(f"UseCase init time: {t_init - t_imports:.4f}s", flush=True)

# Let's measure model/corpus loading on first retrieval execution
t_retrieval_start = time.perf_counter()

# Step 1: Dimensions
dimensions = uc._domain_router.route(req)
domains_queried = [d.legal_domain for d in dimensions]

# Step 2: Targeted queries
targeted_queries = uc._query_builder.build_queries(req, dimensions)
t_builder = time.perf_counter()

print(f"Domain router & query builder time: {t_builder - t_init:.4f}s", flush=True)
print(f"Targeted queries count: {len(targeted_queries)}", flush=True)

retrieval_uc = uc._make_retrieval_use_case()

# Measure targeted queries individually
all_raw_results = []
chunk_dimension_map = {}

t_dim_start = time.perf_counter()
for i, tq in enumerate(targeted_queries):
    td0 = time.perf_counter()
    retrieval_output = retrieval_uc.execute(
        query=tq.query_text,
        top_k=5,
        jurisdiction=req.jurisdiction,
        domain=tq.legal_domain,
    )
    td1 = time.perf_counter()
    print(f"  Dimension {i+1} [{tq.dimension}] ({tq.legal_domain}): {td1 - td0:.4f}s", flush=True)
    for result in retrieval_output.get("results", []):
        cid = result.get("chunk_id") or ""
        if cid not in chunk_dimension_map:
            chunk_dimension_map[cid] = tq.dimension
        all_raw_results.append(result)

t_dim_end = time.perf_counter()
print(f"Total targeted retrieval time across {len(targeted_queries)} queries: {t_dim_end - t_dim_start:.4f}s", flush=True)

# Step 4: Deduplicate
t_dedup0 = time.perf_counter()
seen_chunk_ids = set()
deduplicated_results = []
for result in all_raw_results:
    cid = result.get("chunk_id") or ""
    if cid and cid in seen_chunk_ids:
        continue
    deduplicated_results.append(result)
    if cid:
        seen_chunk_ids.add(cid)
t_dedup1 = time.perf_counter()

# Step 5: Combined evaluation
combined_assessment = EvidenceEvaluator.evaluate(
    results=deduplicated_results,
    query=f"product analysis {req.product_name}",
    jurisdiction=req.jurisdiction,
    domain=None,
)
t_eval = time.perf_counter()
print(f"Evidence evaluation time: {t_eval - t_dedup1:.4f}s", flush=True)

# Step 7: Selection
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
t_sel = time.perf_counter()
print(f"Evidence selection time: {t_sel - t_eval:.4f}s", flush=True)

# Step 8: Select LLM evidence
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

# Step 9: Build prompt
from src.features.product_analysis.domain.analysis_prompt import (
    build_product_evidence_block,
    build_product_analysis_prompt,
)
evidence_block = build_product_evidence_block(llm_evidence)
system_prompt, user_prompt = build_product_analysis_prompt(
    req, evidence_block, domains_queried
)
t_prompt = time.perf_counter()
print(f"Prompt building time: {t_prompt - t_sel:.4f}s", flush=True)
print(f"System prompt length: {len(system_prompt)} chars, User prompt length: {len(user_prompt)} chars", flush=True)

# Step 10: LLM completion
llm = uc._get_llm()
t_llm0 = time.perf_counter()
raw_answer = llm.complete(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    max_tokens=4000,
    response_format={"type": "json_object"},
    timeout_seconds=45,
)
t_llm1 = time.perf_counter()
print(f"LLM request completion time: {t_llm1 - t_llm0:.4f}s", flush=True)
print(f"Raw answer length: {len(raw_answer)} chars", flush=True)

# Step 11: Response parsing
t_parse0 = time.perf_counter()
parsed = parse_structured_analysis_response(raw_answer, valid_citation_ids)
t_parse1 = time.perf_counter()
print(f"Response parsing time: {t_parse1 - t_parse0:.4f}s", flush=True)

# Total Python time
t_total = time.perf_counter() - t0
print(f"TOTAL Python Execution Time: {t_total:.4f}s", flush=True)
