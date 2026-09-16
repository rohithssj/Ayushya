import os
import sys
import time

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
from src.features.product_analysis.domain.analysis_prompt import build_product_analysis_prompt
from src.features.rag.infrastructure.openrouter_provider import OpenRouterProvider

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
domains_queried = [d.legal_domain for d in dimensions]
targeted_queries = uc._query_builder.build_queries(req, dimensions)
retrieval_uc = uc._make_retrieval_use_case()
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

def build_optimized_evidence_block(evidence_items, max_text_len=1200):
    lines = []
    for i, ev in enumerate(evidence_items, 1):
        cit = ev.get("citation", {})
        text = ev.get("text", "").strip()
        if len(text) > max_text_len:
            text = text[:max_text_len] + "..."
        lines.append(f"--- EVIDENCE {i} ---")
        lines.append(f"citation_id: {cit.get('citation_id', '')}")
        lines.append(f"title: {cit.get('title', '')}")
        if cit.get("section"):
            lines.append(f"section: {cit['section']}")
        if cit.get("section_title"):
            lines.append(f"section_title: {cit['section_title']}")
        if cit.get("subsection"):
            lines.append(f"subsection: {cit['subsection']}")
        if cit.get("jurisdiction"):
            lines.append(f"jurisdiction: {cit['jurisdiction']}")
        lines.append(f"text: {text}")
        lines.append("")
    return "\n".join(lines)

opt_evidence_block = build_optimized_evidence_block(llm_evidence)
system_prompt, user_prompt = build_product_analysis_prompt(
    req, opt_evidence_block, domains_queried
)

models_to_test = [
    "mistralai/mistral-small-24b-instruct-2501",
    "meta-llama/llama-3.3-70b-instruct",
]

for m in models_to_test:
    provider = OpenRouterProvider(model=m, fallback_models=[])
    t0 = time.perf_counter()
    try:
        raw_answer = provider.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=1500,
            response_format={"type": "json_object"},
            timeout_seconds=25,
        )
        t1 = time.perf_counter()
        from src.features.product_analysis.application.structured_response_parser import parse_structured_analysis_response
        parsed = parse_structured_analysis_response(raw_answer, valid_citation_ids)
        cits = parsed.get("citations", [])
        print(f"Model [{m}] complete in {t1-t0:.2f}s | JSON parsed OK! | Valid citations: {len(cits)}", flush=True)
    except Exception as e:
        t1 = time.perf_counter()
        print(f"Model [{m}] failed in {t1-t0:.2f}s: {e}", flush=True)
