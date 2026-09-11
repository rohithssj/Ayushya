"""
Product Analysis — CLI bridge for the /api/analysis route.

Called by the Next.js /api/analysis route via execFile.
Reads the full product payload as a JSON string from --payload argument.
Reads OPENROUTER_API_KEY and LLM_MODEL from the process environment.
Prints the structured analysis result as JSON to stdout.
Never logs API keys, full product formulations, or raw provider errors to stdout.

This script is SEPARATE from grounded_answer_api.py, which remains unchanged
and is used exclusively by /api/chat.
"""

import argparse
import json
import os
import sys

# Ensure project root is on the Python path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from src.features.product_analysis.domain.product_request import (
    validate_product_request,
    ProductRequestValidationError,
)
from src.features.product_analysis.application.product_analysis_use_case import (
    ProductAnalysisUseCase,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI bridge for Product Analysis API"
    )
    parser.add_argument(
        "--payload",
        required=False,
        default=None,
        help="JSON-encoded product analysis request payload",
    )
    parser.add_argument(
        "--analysis-id",
        default=None,
        help="Analysis ID (optional; generated if not provided)",
    )
    args = parser.parse_args()

    # ── Parse payload ──────────────────────────────────────────────────────
    payload_str = args.payload or os.environ.get("PRODUCT_PAYLOAD")
    if not payload_str:
        error_res = {
            "error": "missing_payload",
            "error_message": "Missing product payload.",
        }
        print(json.dumps(error_res, ensure_ascii=True), file=sys.stderr)
        sys.exit(1)

    try:
        raw_payload = json.loads(payload_str)
    except (json.JSONDecodeError, ValueError) as e:
        error_res = {
            "error": "invalid_payload",
            "error_message": "Malformed JSON payload.",
        }
        print(json.dumps(error_res, ensure_ascii=True), file=sys.stderr)
        sys.exit(1)

    # ── Validate request ──────────────────────────────────────────────────
    try:
        request = validate_product_request(raw_payload)
    except ProductRequestValidationError as e:
        error_res = {
            "error": "validation_error",
            "error_message": str(e),
        }
        print(json.dumps(error_res, ensure_ascii=True), file=sys.stderr)
        sys.exit(1)

    # ── Execute analysis ──────────────────────────────────────────────────
    try:
        use_case = ProductAnalysisUseCase(base_dir)
        result = use_case.execute(
            request=request,
            analysis_id=args.analysis_id,
        )
        print(json.dumps(result, ensure_ascii=True))
    except Exception as e:
        # Application-level error — never expose internal stack traces to stdout
        error_res = {
            "error": "analysis_failed",
            "error_message": f"Product analysis failed: {type(e).__name__}",
        }
        # Only log to stderr (not surfaced to client)
        print(f"[product_analysis_api] Internal error: {e}", file=sys.stderr)
        print(json.dumps(error_res, ensure_ascii=True), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
