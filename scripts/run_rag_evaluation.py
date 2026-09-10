"""
Phase 9 — Run RAG Evaluation Suite CLI Script.

Executes evaluation across all 18 benchmark dataset cases, prints a human-readable
Markdown evaluation table, and saves a machine-readable JSON report to:
  data/evaluation/rag_evaluation_report.json
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

from src.features.rag.application.run_rag_evaluation_use_case import RunRAGEvaluationUseCase
from src.features.rag.tests.test_rag_evaluation import MockLLMProvider


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AYUSHYA RAG Evaluation Suite")
    parser.add_argument(
        "--live-provider",
        action="store_true",
        help="Use live OpenRouter provider instead of deterministic mock",
    )
    parser.add_argument(
        "--output-json",
        default=os.path.join(base_dir, "data", "evaluation", "rag_evaluation_report.json"),
        help="Output JSON report file path",
    )
    args = parser.parse_args()

    llm_provider = None
    if not args.live_provider:
        llm_provider = MockLLMProvider()

    use_case = RunRAGEvaluationUseCase(base_dir=base_dir, llm_provider=llm_provider)

    print("=" * 80)
    print("AYUSHYA RAG EVALUATION SUITE — RUNNING 18 BENCHMARK CASES")
    print(f"LLM Provider: {'OpenRouter (Live)' if args.live_provider else 'Mocked (Deterministic)'}")
    print("=" * 80)

    report = use_case.execute(top_k=5)

    print("\n" + "=" * 80)
    print("EVALUATION RESULTS BY CASE")
    print("=" * 80)

    header = f"| {'ID':<8} | {'Category':<24} | {'Retr':<5} | {'Evid':<5} | {'Cite':<5} | {'Grnd':<5} | {'Abst':<5} | {'Align':<5} | {'Status':<6} |"
    divider = f"|{'-'*10}|{'-'*26}|{'-'*7}|{'-'*7}|{'-'*7}|{'-'*7}|{'-'*7}|{'-'*7}|{'-'*8}|"
    print(header)
    print(divider)

    for res in report.test_results:
        def symbol(p: bool) -> str:
            return "PASS" if p else "FAIL"

        row = (
            f"| {res.test_id:<8} "
            f"| {res.category[:24]:<24} "
            f"| {symbol(res.retrieval_relevance.passed):<5} "
            f"| {symbol(res.evidence_quality.passed):<5} "
            f"| {symbol(res.citation_correctness.passed):<5} "
            f"| {symbol(res.groundedness.passed):<5} "
            f"| {symbol(res.abstention_safety.passed):<5} "
            f"| {symbol(res.jurisdiction_alignment.passed):<5} "
            f"| {'PASS' if res.passed else 'FAIL':<6} |"
        )
        print(row)

    print(divider)

    print("\n" + "=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    print(f"Total Test Cases   : {report.total_cases}")
    print(f"Passed Cases       : {report.passed_cases}")
    print(f"Failed Cases       : {report.failed_cases}")
    print(f"Pass Rate          : {report.pass_rate_pct:.1f}%")
    print("-" * 40)
    print(f"Retrieval Failures : {report.retrieval_failures}")
    print(f"Evidence Failures  : {report.evidence_failures}")
    print(f"Citation Failures  : {report.citation_failures}")
    print(f"Grounding Failures : {report.grounding_failures}")
    print(f"Abstention Failures: {report.abstention_failures}")
    print(f"Alignment Failures : {report.jurisdiction_failures}")
    print("=" * 80)

    # Save JSON report
    report_dict = report.to_dict()
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    print(f"\nReport saved to: {args.output_json}")


if __name__ == "__main__":
    main()
