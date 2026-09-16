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

print("Testing OpenRouterProvider...", flush=True)
llm = OpenRouterProvider()
print(f"Primary model: {llm.model}", flush=True)
print(f"Fallback models: {llm.fallback_models}", flush=True)

t0 = time.perf_counter()
try:
    res = llm.complete(
        system_prompt="You are a helpful legal assistant.",
        user_prompt="Say Hello in one word.",
        max_tokens=20,
        timeout_seconds=15,
    )
    t1 = time.perf_counter()
    print(f"Response ({t1-t0:.2f}s): {res}", flush=True)
except Exception as e:
    t1 = time.perf_counter()
    print(f"Error ({t1-t0:.2f}s): {type(e).__name__}: {e}", flush=True)
