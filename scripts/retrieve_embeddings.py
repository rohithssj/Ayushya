import argparse
import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.rag.application.retrieve_embeddings_use_case import RetrieveEmbeddingsUseCase


def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic retrieval over AYUSHYA legal embeddings")
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--jurisdiction")
    parser.add_argument("--domain")
    args = parser.parse_args()
    result = RetrieveEmbeddingsUseCase(base_dir).execute(
        query=args.query,
        top_k=args.top_k,
        jurisdiction=args.jurisdiction,
        domain=args.domain,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()