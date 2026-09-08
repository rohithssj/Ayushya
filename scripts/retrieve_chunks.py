import argparse
import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.rag.application.retrieve_chunks_use_case import RetrieveChunksUseCase


def main() -> None:
    parser = argparse.ArgumentParser(description="AYUSHYA retrieval over processed legal chunks")
    parser.add_argument("query", help="User query to search for")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to return")
    parser.add_argument("--jurisdiction", help="Optional exact jurisdiction filter")
    parser.add_argument("--domain", help="Optional exact domain filter")
    args = parser.parse_args()

    result = RetrieveChunksUseCase(base_dir).execute(
        query=args.query,
        top_k=args.top_k,
        jurisdiction=args.jurisdiction,
        domain=args.domain,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()