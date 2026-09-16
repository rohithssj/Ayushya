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

from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase

t_imports = time.perf_counter()
print(f"Python import time: {t_imports - t0:.4f}s", flush=True)

uc = GroundedAnswerUseCase(base_dir)

t_init = time.perf_counter()
print(f"UseCase init time: {t_init - t_imports:.4f}s", flush=True)

query = "Can I patent an herbal mixture under Indian law?"
jurisdiction = "India"

t_ret0 = time.perf_counter()
retrieval_output = uc._retrieval.execute(
    query=query,
    top_k=5,
    jurisdiction=jurisdiction,
    domain=None,
)
t_ret1 = time.perf_counter()
print(f"Hybrid retrieval time: {t_ret1 - t_ret0:.4f}s", flush=True)

t_sel0 = time.perf_counter()
retrieval_output = uc._evidence_selector.execute(retrieval_output)
selected_evidence = retrieval_output.get("evidence", {}).get("selected", [])
t_sel1 = time.perf_counter()
print(f"Evidence selection time: {t_sel1 - t_sel0:.4f}s", flush=True)

from src.features.rag.domain.grounded_answer import build_evidence_block, build_grounding_prompt, extract_citation_ids

evidence_block = build_evidence_block(selected_evidence)
system_prompt, user_prompt = build_grounding_prompt(query, evidence_block)
t_prompt = time.perf_counter()
print(f"Prompt building time: {t_prompt - t_sel1:.4f}s", flush=True)
print(f"System prompt length: {len(system_prompt)} chars, User prompt length: {len(user_prompt)} chars", flush=True)

llm = uc._get_llm()
t_llm0 = time.perf_counter()
raw_answer = llm.complete(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    timeout_seconds=15,
)
t_llm1 = time.perf_counter()
print(f"LLM request completion time: {t_llm1 - t_llm0:.4f}s", flush=True)
print(f"Raw answer length: {len(raw_answer)} chars", flush=True)

t_cite0 = time.perf_counter()
valid_citation_ids = {
    ev.get("citation", {}).get("citation_id", "")
    for ev in selected_evidence
    if ev.get("citation", {}).get("citation_id")
}
validated_citations = extract_citation_ids(raw_answer, valid_citation_ids)
t_cite1 = time.perf_counter()
print(f"Citation validation time: {t_cite1 - t_cite0:.4f}s", flush=True)

t_total = time.perf_counter() - t0
print(f"TOTAL Chat Python Execution Time: {t_total:.4f}s", flush=True)
