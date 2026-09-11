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

from src.features.rag.infrastructure.openrouter_provider import OpenRouterProvider, LLMProviderError

llm = OpenRouterProvider()
print(f"Primary Model: {llm.model}")
print(f"Fallback Models: {llm.fallback_models}")

try:
    resp = llm.complete("You are a helpful assistant.", "Say hello in JSON format: {\"message\": \"...\"}", response_format={"type": "json_object"})
    print("Response:", resp)
except LLMProviderError as e:
    print("LLM Error:", type(e).__name__, str(e))
