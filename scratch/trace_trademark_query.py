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

from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase
from src.features.rag.application.hybrid_retrieval_use_case import HybridRetrievalUseCase

uc_retrieval = HybridRetrievalUseCase(base_dir)

query = "Can I register a trademark for the brand name of my Ayurvedic medicine?"
print("=== RETRIEVAL TRACE FOR TRADEMARK QUERY ===")
print("Query:", query)

res = uc_retrieval.execute(query=query, top_k=10, jurisdiction="India")

print("\nTop 10 Retrieved Chunks:")
for i, r in enumerate(res.get("results", []), 1):
    print(f"  {i}. [{r.get('chunk_id')}] doc={r.get('document_id')} sec={r.get('section')} score={r.get('relevance_score')}")
    print(f"     Title: {r.get('title')}")
    print(f"     Snippet: {r.get('text', '')[:150].replace('\n', ' ')}...")

uc_grounded = GroundedAnswerUseCase(base_dir)
res_grounded = uc_grounded.execute(query=query, jurisdiction="India", top_k=5)

print("\n=== GROUNDED ANSWER RESULT ===")
print("Abstained:", res_grounded.get("abstained"))
print("Evidence Strength:", res_grounded.get("evidence_strength"))
print("Citations:", res_grounded.get("citations"))
print("\nAnswer:")
print(res_grounded.get("answer"))
