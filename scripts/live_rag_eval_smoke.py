"""
Phase 9 — Live OpenRouter Provider Smoke Test Script.

Runs a small sample of non-sensitive benchmark queries through the full pipeline
with the live OpenRouter provider.

Separated from the automated test suite so live provider availability is not required
for passing unit tests.
"""

import json
import os
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

# Load .env.local if present
env_local = base_dir / ".env.local"
if env_local.exists():
    for line in env_local.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            os.environ[k.strip()] = v.strip()

from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase
from src.features.rag.domain.rag_evaluator import RAGEvaluator


def main() -> None:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("SKIP: OPENROUTER_API_KEY is not set. Skipping live provider smoke test.")
        return

    sample_cases = [
        {
            "id": "EVAL_001",
            "category": "Patents",
            "query": "Can a simple mixture of known herbal ingredients with no synergistic effect be patented under Indian patent law?",
            "expected_jurisdiction": "India",
            "expected_domain": "patents",
            "should_have_sufficient_evidence": True,
            "expected_abstention": False,
            "expected_keywords": ["patent", "admixture", "component"],
        },
        {
            "id": "EVAL_002",
            "category": "Biodiversity / ABS",
            "query": "What approval is required from the National Biodiversity Authority before applying for IP protection on biological resources?",
            "expected_jurisdiction": "India",
            "expected_domain": "biodiversity",
            "should_have_sufficient_evidence": True,
            "expected_abstention": False,
            "expected_keywords": ["biodiversity", "approval"],
        },
        {
            "id": "EVAL_011",
            "category": "TRIPS",
            "query": "What does Article 27 of the TRIPS Agreement state regarding patentable subject matter and exceptions?",
            "expected_jurisdiction": "International",
            "expected_domain": "trips",
            "should_have_sufficient_evidence": True,
            "expected_abstention": False,
            "expected_keywords": ["trips", "patent", "article"],
        },
        {
            "id": "EVAL_015",
            "category": "Unsupported",
            "query": "What are the legal requirements for filing a quantum computing satellite patent in outer space under US ERISA pension law?",
            "expected_jurisdiction": "International",
            "expected_domain": "unsupported",
            "should_have_sufficient_evidence": False,
            "expected_abstention": True,
            "expected_keywords": [],
        },
    ]

    use_case = GroundedAnswerUseCase(base_dir=str(base_dir))

    print("=" * 80)
    print("LIVE OPENROUTER PROVIDER SMOKE TEST (4 SAMPLE QUERIES)")
    print("=" * 80)

    for case in sample_cases:
        print(f"\n[Case {case['id']}] {case['category']}: {case['query']}")
        dom = case["expected_domain"] if case["expected_domain"] != "unsupported" else None
        output = use_case.execute(
            query=case["query"],
            jurisdiction=case["expected_jurisdiction"],
            domain=dom,
            top_k=3,
        )

        res = RAGEvaluator.evaluate_case(case, output)

        print(f"  Abstained      : {output.get('abstained')}")
        print(f"  Evidence Str   : {output.get('evidence_strength')}")
        print(f"  Citations      : {output.get('citations')}")
        print(f"  Passed Metrics : {'PASS' if res.passed else 'FAIL'}")
        if output.get("answer"):
            ans_snippet = output["answer"][:120].replace("\n", " ")
            print(f"  Answer Snippet : {ans_snippet}...")
        elif output.get("abstained"):
            print(f"  Abstain Reason : {output.get('abstention_reason')}")

    print("\n" + "=" * 80)
    print("LIVE SMOKE TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
