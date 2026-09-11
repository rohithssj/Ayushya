import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.rag.application.hybrid_retrieval_use_case import HybridRetrievalUseCase

print("=== 1. SEARCHING WITH JURISDICTION=NONE ===")
uc = HybridRetrievalUseCase(base_dir)
res_no_jur = uc.execute(query="What does the TRIPS Agreement require regarding patent protection?", top_k=10, jurisdiction=None)

print("Top 10 results (jurisdiction=None):")
for i, r in enumerate(res_no_jur.get("results", []), 1):
    print(f"  {i}. [{r.get('chunk_id')}] doc={r.get('document_id')} domain={r.get('domain')} jur={r.get('jurisdiction')} sec={r.get('section')} score={r.get('relevance_score')}")

print("\n=== 2. SEARCHING WITH JURISDICTION='India' (Default in frontend UI if user selects India!) ===")
res_india = uc.execute(query="What does the TRIPS Agreement require regarding patent protection?", top_k=10, jurisdiction="India")

print("Top 10 results (jurisdiction='India'):")
for i, r in enumerate(res_india.get("results", []), 1):
    print(f"  {i}. [{r.get('chunk_id')}] doc={r.get('document_id')} domain={r.get('domain')} jur={r.get('jurisdiction')} sec={r.get('section')} score={r.get('relevance_score')}")

print("\n=== 3. SEARCHING WITH JURISDICTION='International' ===")
res_intl = uc.execute(query="What does the TRIPS Agreement require regarding patent protection?", top_k=10, jurisdiction="International")

print("Top 10 results (jurisdiction='International'):")
for i, r in enumerate(res_intl.get("results", []), 1):
    print(f"  {i}. [{r.get('chunk_id')}] doc={r.get('document_id')} domain={r.get('domain')} jur={r.get('jurisdiction')} sec={r.get('section')} score={r.get('relevance_score')}")
