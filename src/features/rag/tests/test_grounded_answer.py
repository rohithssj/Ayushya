"""
Phase 8 — Grounded Answer: deterministic unit tests with mocked LLM provider.

No live OpenRouter API calls. All LLM responses are synthetic.
Tests cover all specified scenarios.
"""

import unittest
from unittest.mock import MagicMock, patch
from typing import Any, Dict, List, Optional, Set

from src.features.rag.domain.grounded_answer import (
    GroundedAnswer,
    AbstentionResponse,
    build_evidence_block,
    build_grounding_prompt,
    extract_citation_ids,
    validate_citations,
)
from src.features.rag.infrastructure.openrouter_provider import (
    LLMAuthError,
    LLMConfigError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
    LLMUnavailableError,
    OpenRouterProvider,
)


# ---------------------------------------------------------------------------
# Shared synthetic test data
# ---------------------------------------------------------------------------

def _make_selected_evidence(
    chunk_id: str = "c001",
    citation_id: str = "cit_abc123",
    title: str = "The Patents Act, 1970",
    section: str = "Section 3",
    text: str = (
        "The following shall not be inventions within the meaning of this Act: "
        "a substance obtained by a mere admixture resulting only in the aggregation "
        "of the properties of the components thereof."
    ),
) -> Dict[str, Any]:
    return {
        "evidence_id": "ev_001",
        "chunk_id": chunk_id,
        "text": text,
        "citation": {
            "citation_id": citation_id,
            "chunk_id": chunk_id,
            "document_id": "patents_act_1970",
            "title": title,
            "section": section,
            "section_title": "Non-patentable inventions",
            "subsection": "3(d)",
            "chapter": "Chapter II",
            "page_start": 12,
            "page_end": 13,
            "jurisdiction": "india",
            "domain": "patents",
            "authority": "Parliament of India",
            "year": 1970,
            "source_url": None,
        },
        "selection_reason": "Hybrid rank 1; dual lexical+semantic match.",
    }


def _strong_assessment() -> Dict[str, Any]:
    return {
        "strength": "strong",
        "abstention_recommended": False,
        "requires_human_review": False,
        "reasons": ["Found 1 substantive legal result(s)."],
    }


def _insufficient_assessment() -> Dict[str, Any]:
    return {
        "strength": "insufficient",
        "abstention_recommended": True,
        "requires_human_review": True,
        "reasons": ["Zero retrieval results returned."],
    }


def _make_retrieval_output(
    selected: List[Dict[str, Any]],
    assessment: Dict[str, Any],
    strength: Optional[str] = None,
) -> Dict[str, Any]:
    st = strength or assessment["strength"]
    return {
        "query": "test query",
        "jurisdiction_filter": "india",
        "domain_filter": "patents",
        "retrieval_method": "hybrid_rrf",
        "top_k": 5,
        "evidence_strength": st,
        "abstention_recommended": assessment["abstention_recommended"],
        "requires_human_review": assessment["requires_human_review"],
        "evidence_assessment": assessment,
        "results": [],
        "evidence": {"selected": selected, "count": len(selected)},
    }


# ---------------------------------------------------------------------------
# Helper: run the use-case execute() with mocked retrieval + selector
# ---------------------------------------------------------------------------

def _run_use_case(
    retrieval_output: Dict[str, Any],
    llm_response: Optional[str] = None,
    llm_error: Optional[Exception] = None,
) -> Dict[str, Any]:
    """
    Run GroundedAnswerUseCase.execute() with fully mocked retrieval and LLM.
    """
    from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase

    # Mock retrieval use case
    mock_retrieval = MagicMock()
    mock_retrieval.execute.return_value = {
        k: v for k, v in retrieval_output.items()
        if k != "evidence"  # evidence added by selector
    }

    # Mock evidence selector to return full output
    mock_selector = MagicMock()
    mock_selector.execute.return_value = retrieval_output

    # Mock LLM provider
    mock_llm = MagicMock()
    if llm_error:
        mock_llm.complete.side_effect = llm_error
    else:
        mock_llm.complete.return_value = llm_response or ""

    use_case = GroundedAnswerUseCase.__new__(GroundedAnswerUseCase)
    use_case._retrieval = mock_retrieval
    use_case._evidence_selector = mock_selector
    use_case._llm = mock_llm

    return use_case.execute(
        query="test query",
        jurisdiction="india",
        domain="patents",
        request_id="req_test001",
    )


# ===========================================================================
# 1. Successful grounded response
# ===========================================================================
class TestSuccessfulGroundedResponse(unittest.TestCase):
    def test_returns_answer_with_citations(self):
        ev = _make_selected_evidence()
        output = _make_retrieval_output([ev], _strong_assessment())
        llm_text = (
            "Based on the evidence (cit_abc123), Section 3 of The Patents Act, 1970 "
            "provides that a substance obtained by mere admixture is not patentable. "
            "Please consult a qualified patent attorney for binding advice."
        )
        result = _run_use_case(output, llm_response=llm_text)

        self.assertFalse(result["abstained"])
        self.assertIsNotNone(result["answer"])
        self.assertIn("cit_abc123", result["citations"])
        self.assertEqual(result["evidence_strength"], "strong")
        self.assertFalse(result.get("error"))

    def test_answer_text_preserved(self):
        ev = _make_selected_evidence()
        output = _make_retrieval_output([ev], _strong_assessment())
        llm_text = "According to cit_abc123, admixtures are not patentable."
        result = _run_use_case(output, llm_response=llm_text)
        self.assertEqual(result["answer"], llm_text)

    def test_evidence_section_present(self):
        ev = _make_selected_evidence()
        output = _make_retrieval_output([ev], _strong_assessment())
        result = _run_use_case(output, llm_response="Answer referencing cit_abc123.")
        self.assertIn("evidence", result)
        self.assertEqual(result["evidence"]["count"], 1)


# ===========================================================================
# 2. Abstention prevents LLM invocation
# ===========================================================================
class TestAbstentionPreventsLLM(unittest.TestCase):
    def test_abstention_returns_no_answer(self):
        output = _make_retrieval_output([], _insufficient_assessment())
        result = _run_use_case(output, llm_response="Should never see this")
        self.assertTrue(result["abstained"])
        self.assertIsNone(result["answer"])

    def test_abstention_llm_not_called(self):
        from src.features.rag.application.grounded_answer_use_case import GroundedAnswerUseCase
        output = _make_retrieval_output([], _insufficient_assessment())

        mock_retrieval = MagicMock()
        mock_retrieval.execute.return_value = {k: v for k, v in output.items() if k != "evidence"}
        mock_selector = MagicMock()
        mock_selector.execute.return_value = output
        mock_llm = MagicMock()

        use_case = GroundedAnswerUseCase.__new__(GroundedAnswerUseCase)
        use_case._retrieval = mock_retrieval
        use_case._evidence_selector = mock_selector
        use_case._llm = mock_llm

        use_case.execute(query="q", jurisdiction="india", request_id="r1")
        mock_llm.complete.assert_not_called()

    def test_abstention_reason_preserved(self):
        output = _make_retrieval_output([], _insufficient_assessment())
        result = _run_use_case(output)
        self.assertIsNotNone(result["abstention_reason"])
        self.assertTrue(len(result["abstention_reason"]) > 0)

    def test_requires_human_review_on_abstention(self):
        output = _make_retrieval_output([], _insufficient_assessment())
        result = _run_use_case(output)
        self.assertTrue(result["requires_human_review"])


# ===========================================================================
# 3. Insufficient evidence prevents LLM invocation
# ===========================================================================
class TestInsufficientEvidencePreventsLLM(unittest.TestCase):
    def test_insufficient_strength_abstains(self):
        assessment = {
            "strength": "insufficient",
            "abstention_recommended": True,
            "requires_human_review": True,
            "reasons": ["Score below threshold."],
        }
        output = _make_retrieval_output([], assessment)
        result = _run_use_case(output)
        self.assertTrue(result["abstained"])
        self.assertEqual(result["evidence_strength"], "insufficient")

    def test_empty_selected_evidence_abstains(self):
        # Even if strength says "strong", no evidence → abstain
        assessment = _strong_assessment()
        output = _make_retrieval_output([], assessment)
        result = _run_use_case(output)
        self.assertTrue(result["abstained"])


# ===========================================================================
# 4. Invalid citation ID (not in evidence)
# ===========================================================================
class TestInvalidCitationId(unittest.TestCase):
    def test_fabricated_citation_id_excluded(self):
        ev = _make_selected_evidence(citation_id="cit_abc123")
        output = _make_retrieval_output([ev], _strong_assessment())
        # LLM invents a citation_id not in evidence
        llm_text = "According to cit_FABRICATED, some rule applies."
        result = _run_use_case(output, llm_response=llm_text)
        self.assertNotIn("cit_FABRICATED", result["citations"])

    def test_valid_and_invalid_mixed(self):
        ev = _make_selected_evidence(citation_id="cit_abc123")
        output = _make_retrieval_output([ev], _strong_assessment())
        llm_text = "See cit_abc123 and also cit_MADE_UP for details."
        result = _run_use_case(output, llm_response=llm_text)
        self.assertIn("cit_abc123", result["citations"])
        self.assertNotIn("cit_MADE_UP", result["citations"])


# ===========================================================================
# 5. Valid citation IDs
# ===========================================================================
class TestValidCitationIds(unittest.TestCase):
    def test_all_valid_ids_collected(self):
        ev1 = _make_selected_evidence(chunk_id="c001", citation_id="cit_aaa")
        ev2 = _make_selected_evidence(chunk_id="c002", citation_id="cit_bbb",
                                       section="Section 5", text="A patent application shall be made.")
        output = _make_retrieval_output([ev1, ev2], _strong_assessment())
        llm_text = "Evidence cit_aaa and cit_bbb both support this conclusion."
        result = _run_use_case(output, llm_response=llm_text)
        self.assertIn("cit_aaa", result["citations"])
        self.assertIn("cit_bbb", result["citations"])

    def test_citations_list_is_sorted_deterministic(self):
        ev1 = _make_selected_evidence(chunk_id="c001", citation_id="cit_zzz")
        ev2 = _make_selected_evidence(chunk_id="c002", citation_id="cit_aaa",
                                       section="Section 5", text="Patent application form.")
        output = _make_retrieval_output([ev1, ev2], _strong_assessment())
        llm_text = "See cit_zzz and cit_aaa."
        result = _run_use_case(output, llm_response=llm_text)
        # Sorted → deterministic
        self.assertEqual(result["citations"], sorted(result["citations"]))


# ===========================================================================
# 6. Empty model response
# ===========================================================================
class TestEmptyModelResponse(unittest.TestCase):
    def test_empty_response_returns_provider_error(self):
        ev = _make_selected_evidence()
        output = _make_retrieval_output([ev], _strong_assessment())
        result = _run_use_case(output, llm_error=LLMResponseError("Empty response."))
        self.assertEqual(result.get("error"), "llm_provider_error")
        self.assertIsNone(result["answer"])


# ===========================================================================
# 7. Provider error
# ===========================================================================
class TestProviderErrors(unittest.TestCase):
    def _test_error(self, exc):
        ev = _make_selected_evidence()
        output = _make_retrieval_output([ev], _strong_assessment())
        result = _run_use_case(output, llm_error=exc)
        self.assertEqual(result.get("error"), "llm_provider_error")
        self.assertIsNone(result["answer"])
        self.assertFalse(result["abstained"])
        self.assertTrue(result["requires_human_review"])

    def test_rate_limit_error(self):
        self._test_error(LLMRateLimitError("Rate limited."))

    def test_auth_error(self):
        self._test_error(LLMAuthError("Auth failed."))

    def test_timeout_error(self):
        self._test_error(LLMTimeoutError("Timeout."))

    def test_unavailable_error(self):
        self._test_error(LLMUnavailableError("Service down."))


# ===========================================================================
# 8. Missing configuration (no API key)
# ===========================================================================
class TestMissingConfiguration(unittest.TestCase):
    def test_missing_api_key_raises_config_error(self):
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "", "LLM_MODEL": "some-model"}):
            with self.assertRaises(LLMConfigError):
                OpenRouterProvider()

    def test_explicit_empty_api_key_raises_config_error(self):
        with self.assertRaises(LLMConfigError):
            OpenRouterProvider(api_key="", model="some-model")


# ===========================================================================
# 9. Malformed response
# ===========================================================================
class TestMalformedResponse(unittest.TestCase):
    def test_malformed_response_returns_error(self):
        ev = _make_selected_evidence()
        output = _make_retrieval_output([ev], _strong_assessment())
        result = _run_use_case(output, llm_error=LLMResponseError("Malformed JSON."))
        self.assertEqual(result.get("error"), "llm_provider_error")


# ===========================================================================
# Domain unit tests: extract_citation_ids and validate_citations
# ===========================================================================
class TestCitationExtractionUnit(unittest.TestCase):
    def test_extracts_present_ids(self):
        text = "See cit_abc and cit_def for details."
        valid = {"cit_abc", "cit_def", "cit_xyz"}
        found = extract_citation_ids(text, valid)
        self.assertIn("cit_abc", found)
        self.assertIn("cit_def", found)

    def test_does_not_extract_absent_ids(self):
        text = "No citation here."
        valid = {"cit_abc"}
        found = extract_citation_ids(text, valid)
        self.assertEqual(found, [])

    def test_validate_citations_removes_invalid(self):
        raw = ["cit_real", "cit_FAKE"]
        valid = {"cit_real"}
        result = validate_citations(raw, valid)
        self.assertEqual(result, ["cit_real"])

    def test_validate_citations_all_valid(self):
        raw = ["cit_a", "cit_b"]
        valid = {"cit_a", "cit_b"}
        result = validate_citations(raw, valid)
        self.assertCountEqual(result, ["cit_a", "cit_b"])

    def test_extract_returns_sorted(self):
        text = "cit_zzz and cit_aaa mentioned."
        valid = {"cit_zzz", "cit_aaa"}
        found = extract_citation_ids(text, valid)
        self.assertEqual(found, sorted(found))


# ===========================================================================
# Domain unit tests: build_evidence_block
# ===========================================================================
class TestEvidenceBlockBuilding(unittest.TestCase):
    def test_includes_citation_id(self):
        ev = _make_selected_evidence(citation_id="cit_abc123")
        block = build_evidence_block([ev])
        self.assertIn("cit_abc123", block)

    def test_includes_text(self):
        ev = _make_selected_evidence(text="Special legal text here.")
        block = build_evidence_block([ev])
        self.assertIn("Special legal text here.", block)

    def test_empty_evidence_block(self):
        block = build_evidence_block([])
        self.assertIn("No evidence", block)

    def test_no_fabricated_fields(self):
        # Source url is None — must not appear as a value
        ev = _make_selected_evidence()
        block = build_evidence_block([ev])
        self.assertNotIn("None", block)  # None should not be printed as a string
        self.assertNotIn("source_url", block)   # source_url omitted when None


# ===========================================================================
# Domain unit tests: build_grounding_prompt
# ===========================================================================
class TestGroundingPrompt(unittest.TestCase):
    def test_returns_two_prompts(self):
        system, user = build_grounding_prompt("test query", "evidence block")
        self.assertIsInstance(system, str)
        self.assertIsInstance(user, str)

    def test_query_in_user_prompt(self):
        _, user = build_grounding_prompt("my special query", "evidence block")
        self.assertIn("my special query", user)

    def test_evidence_in_user_prompt(self):
        _, user = build_grounding_prompt("query", "EVIDENCE_BLOCK_CONTENT")
        self.assertIn("EVIDENCE_BLOCK_CONTENT", user)

    def test_system_prompt_contains_grounding_rules(self):
        system, _ = build_grounding_prompt("query", "evidence")
        self.assertIn("ONLY", system)
        self.assertIn("fabricate", system)
        self.assertIn("citation_id", system)
        self.assertIn("legal advice", system)

    def test_data_use_note_present(self):
        system, _ = build_grounding_prompt("query", "evidence")
        self.assertIn("DATA USE NOTE", system)


# ===========================================================================
# Domain models: GroundedAnswer and AbstentionResponse
# ===========================================================================
class TestDomainModels(unittest.TestCase):
    def test_grounded_answer_to_dict(self):
        ga = GroundedAnswer(
            request_id="r1",
            query="q",
            answer="answer text",
            abstained=False,
            abstention_reason=None,
            evidence_strength="strong",
            requires_human_review=False,
            citations=["cit_abc"],
        )
        d = ga.to_dict()
        self.assertEqual(d["request_id"], "r1")
        self.assertEqual(d["answer"], "answer text")
        self.assertFalse(d["abstained"])
        self.assertEqual(d["citations"], ["cit_abc"])

    def test_abstention_response_to_dict(self):
        ar = AbstentionResponse(
            request_id="r2",
            query="q",
            evidence_strength="insufficient",
            requires_human_review=True,
            abstention_reason="No evidence found.",
        )
        d = ar.to_dict()
        self.assertTrue(d["abstained"])
        self.assertIsNone(d["answer"])
        self.assertEqual(d["citations"], [])
        self.assertEqual(d["abstention_reason"], "No evidence found.")


if __name__ == "__main__":
    unittest.main()
