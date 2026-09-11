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

uc = GroundedAnswerUseCase(base_dir)

print("=== TESTING TRIPS CHAT QUERY (Jurisdiction = International) ===")
res_trips = uc.execute(query="What does the TRIPS Agreement require regarding patent protection?", jurisdiction="International", top_k=5)

print("Abstained:", res_trips.get("abstained"))
print("Evidence Strength:", res_trips.get("evidence_strength"))
print("Citations:", res_trips.get("citations"))
print("\nAnswer (First 300 chars):")
print(str(res_trips.get("answer"))[:300])

print("\nSelected Evidence Items:")
for ev in res_trips.get("evidence", {}).get("selected", []):
    cit = ev.get("citation", {})
    print(f"  - [{cit.get('citation_id')}] doc={cit.get('document_id')} sec={cit.get('section')} title={cit.get('title')}")
