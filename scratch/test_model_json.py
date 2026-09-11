import os
import sys

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

from src.features.rag.infrastructure.openrouter_provider import OpenRouterProvider

sys_prompt = "You are AYUSHYA. Return a JSON object with key 'test': 'hello'."
usr_prompt = "Say hello in JSON."

models = [
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-small-24b-instruct-2501",
    "nvidia/nemotron-3-super-120b-a12b",
]

for m in models:
    print(f"\n--- Testing Model: {m} ---")
    provider = OpenRouterProvider(model=m, fallback_models=[], timeout=15)
    try:
        res1 = provider.complete(sys_prompt, usr_prompt, response_format={"type": "json_object"})
        print("WITH response_format:", res1[:100])
    except Exception as e:
        print("WITH response_format FAILED:", type(e).__name__, str(e))

    try:
        res2 = provider.complete(sys_prompt, usr_prompt, response_format=None)
        print("WITHOUT response_format:", res2[:100])
    except Exception as e:
        print("WITHOUT response_format FAILED:", type(e).__name__, str(e))
