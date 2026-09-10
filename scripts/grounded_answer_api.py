"""
Phase 8 — CLI bridge for Grounded Answer API.

Called by the Next.js /api/chat route via execFile.
Reads OPENROUTER_API_KEY and LLM_MODEL from the process environment.
Never logs API keys or full prompts to stdout.
"""

import argparse
import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI bridge for Grounded Answer API")
    parser.add_argument("--query", required=True, help="User query")
    parser.add_argument("--jurisdiction", default=None, help="Jurisdiction filter")
    parser.add_argument("--domain", default=None, help="Domain filter")
    parser.add_argument("--top-k", type=int, default=5, help="Top K retrieval results")
    parser.add_argument("--request-id", default=None, help="Request ID (optional)")
    args = parser.parse_args()

    jurisdiction = args.jurisdiction if args.jurisdiction and args.jurisdiction.strip() else None
    domain = args.domain if args.domain and args.domain.strip() else None

    try:
        use_case = GroundedAnswerUseCase(base_dir)
        result = use_case.execute(
            query=args.query,
            jurisdiction=jurisdiction,
            domain=domain,
            top_k=args.top_k,
            request_id=args.request_id,
        )
        print(json.dumps(result, ensure_ascii=True))
    except Exception as e:
        error_res = {"error": str(e)}
        print(json.dumps(error_res, ensure_ascii=True), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
