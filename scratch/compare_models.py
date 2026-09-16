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

from src.features.rag.infrastructure.openrouter_provider import OpenRouterProvider

test_models = [
    "nvidia/nemotron-3-super-120b-a12b",
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-small-24b-instruct-2501",
    "google/gemini-2.0-flash-001",
]

sys_p = "You are AYUSHYA legal assistant. Return JSON only."
user_p = "Provide a JSON object with fields grounded_summary and citations for Ashwagandha tablet formulation."

for m in test_models:
    try:
        provider = OpenRouterProvider(model=m, fallback_models=[])
        t0 = time.perf_counter()
        res = provider.complete(sys_p, user_p, max_tokens=300, timeout_seconds=15)
        t1 = time.perf_counter()
        print(f"Model [{m}]: {t1-t0:.2f}s | Output len: {len(res)}", flush=True)
    except Exception as e:
        print(f"Model [{m}]: FAILED ({type(e).__name__}: {e})", flush=True)
