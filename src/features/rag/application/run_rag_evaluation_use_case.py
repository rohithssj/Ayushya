"""
Phase 9 — Run RAG Evaluation Use Case (Application Layer).

Application service that loads the evaluation dataset, runs the queries through
GroundedAnswerUseCase, and compiles an EvaluationSuiteReport via RAGEvaluator.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase
from src.features.rag.domain.rag_evaluator import RAGEvaluator, EvaluationSuiteReport
from src.features.rag.infrastructure.openrouter_provider import OpenRouterProvider


class RunRAGEvaluationUseCase:
    """
    Executes RAG pipeline evaluation across a dataset of test cases.
    """

    def __init__(
        self,
        base_dir: str,
        dataset_path: Optional[str] = None,
        llm_provider: Optional[OpenRouterProvider] = None,
    ) -> None:
        if os.path.basename(base_dir) == "src":
            base_dir = os.path.dirname(base_dir)
        self._base_dir = base_dir
        self._dataset_path = dataset_path or os.path.join(
            base_dir, "data", "evaluation", "rag_evaluation_dataset.json"
        )
        self._llm_provider = llm_provider

    def load_dataset(self) -> List[Dict[str, Any]]:
        with open(self._dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def execute(
        self,
        test_cases: Optional[List[Dict[str, Any]]] = None,
        top_k: int = 5,
    ) -> EvaluationSuiteReport:
        if test_cases is None:
            test_cases = self.load_dataset()

        grounded_use_case = GroundedAnswerUseCase(
            base_dir=self._base_dir,
            llm_provider=self._llm_provider,
        )

        pipeline_outputs: List[Dict[str, Any]] = []

        for case in test_cases:
            query: str = case["query"]
            jur: str = case["expected_jurisdiction"]
            dom: Optional[str] = case.get("expected_domain")
            if dom == "unsupported":
                dom = None  # Do not pass 'unsupported' as a domain filter to retrieval

            output = grounded_use_case.execute(
                query=query,
                jurisdiction=jur,
                domain=dom,
                top_k=top_k,
                request_id=f"eval_{case['id']}",
            )
            pipeline_outputs.append(output)

        report = RAGEvaluator.evaluate_suite(test_cases, pipeline_outputs)
        return report
