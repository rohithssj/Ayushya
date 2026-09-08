import argparse
import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.rag.infrastructure.embedding_generator import EmbeddingGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate local embeddings for AYUSHYA legal chunks")
    parser.add_argument(
        "--model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Sentence-transformers model name",
    )
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()
    result = EmbeddingGenerator(args.model).generate(
        processed_dir=os.path.join(base_dir, "data", "processed"),
        store_dir=os.path.join(base_dir, "data", "embeddings", "legal_chunks"),
        batch_size=args.batch_size,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()